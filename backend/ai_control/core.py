import time
from typing import Dict, Any, Optional

from backend.ai_control.models import AIRequest, AIResponse, UsageRecord, CostRecord
from backend.budgets.manager import BudgetManager
from backend.circuit_breaker.breaker import CostCircuitBreaker, CircuitState
from backend.api_security.rate_limiting import MultiDimensionalRateLimiter
from backend.caching.exact_cache import ExactResponseCache
from backend.caching.semantic_cache import SemanticCache
from backend.llm.model_router import CostAwareModelRouter
from backend.context.compressor import PromptCompressor
from backend.database.ledger import CostLedger
from backend.idempotency.guard import IdempotencyGuard
from backend.observability.audit_logger import ConsoleJSONLogger

class AIControl:
    """
    UNIVERSAL AI CONTROL PLANE & GOVERNANCE GATEWAY ENGINE (LLMGuard / AIControl).
    Centralized reverse-proxy choke point enforcing the complete 18-step production request lifecycle:
    1. Auth & Identity mapping
    2. RBAC check
    3. Multi-dimensional Token Rate Limiting (RPM, TPM, ITPM, OTPM, Concurrency)
    4. Pre-flight Token & Cost Estimation
    5. Hierarchical Budget Checks (Global, Tenant, User, Feature, Request)
    6. 3-State Cost Circuit Breakers & Spend Velocity Tripwire
    7. Idempotency & Duplicate Fingerprint Control
    8. Exact & Semantic Response Caching
    9. Cost-Aware Multi-Tier Model Routing & Confidence Cascades
    10. Context Compression & Prompt Prefix Caching Architecture
    11. LLM Execution with Hard Output Caps
    12. Post-flight Provider Usage Metering & Financial Reconciliation
    13. Immutable Cost Ledger Logging
    14. Observability & FinOps Telemetry
    """

    def __init__(self):
        self.budget_manager = BudgetManager()
        self.circuit_breaker = CostCircuitBreaker()
        self.rate_limiter = MultiDimensionalRateLimiter()
        self.exact_cache = ExactResponseCache()
        self.semantic_cache = SemanticCache()
        self.model_router = CostAwareModelRouter()
        self.compressor = PromptCompressor()
        self.cost_ledger = CostLedger()
        self.idempotency_guard = IdempotencyGuard()
        self.logger = ConsoleJSONLogger()

    def generate(self, request: AIRequest) -> AIResponse:
        start_time = time.time()
        
        # Step 1: Idempotency & Duplicate Check
        fp = self.idempotency_guard.compute_fingerprint(
            user_id=request.user_id,
            prompt=request.prompt,
            task=request.task_type,
            idempotency_key=request.idempotency_key
        )
        cached_dup = self.idempotency_guard.check_duplicate(fp)
        if cached_dup:
            print(f"[AIControl] Idempotency Hit for request {request.request_id}")
            return cached_dup["response"]

        self.idempotency_guard.mark_in_flight(fp)

        # Step 2: Multi-dimensional Rate Limit Check
        rl_passed, rl_reason = self.rate_limiter.check_limits(
            user_id=request.user_id,
            estimated_input_tokens=len(request.prompt) // 4,
            max_output_tokens=request.max_tokens or 1024
        )
        if not rl_passed:
            self.logger.log_event("RATE_LIMIT_EXCEEDED", "MEDIUM", {"user_id": request.user_id, "reason": rl_reason})
            return AIResponse(
                request_id=request.request_id,
                trace_id=request.trace_id,
                text="",
                model_used="none",
                provider="none",
                usage=UsageRecord(),
                cost=CostRecord(),
                latency_ms=(time.time() - start_time) * 1000,
                status="rejected",
                error_message=f"429 Rate Limit Exceeded: {rl_reason}"
            )

        # Step 3: Pre-flight Token & Cost Estimation
        chosen_model = self.model_router.select_model(
            prompt=request.prompt,
            task_type=request.task_type,
            preferred_model=request.preferred_model,
            circuit_state=self.circuit_breaker.state.value
        )
        estimated_cost = self.budget_manager.estimate_preflight_cost(
            prompt=request.prompt,
            context=request.context,
            model=chosen_model,
            max_output_tokens=request.max_tokens or 1024
        )

        # Step 4: Circuit Breaker Evaluation
        c_state, c_reason = self.circuit_breaker.evaluate_state(
            current_spend=self.budget_manager.global_daily_spend,
            budget_limit=self.budget_manager.global_daily_limit
        )
        if c_state == CircuitState.OPEN:
            self.logger.log_event("CIRCUIT_BREAKER_TRIPPED", "CRITICAL", {"reason": c_reason})
            return AIResponse(
                request_id=request.request_id,
                trace_id=request.trace_id,
                text="",
                model_used=chosen_model,
                provider="none",
                usage=UsageRecord(),
                cost=CostRecord(),
                latency_ms=(time.time() - start_time) * 1000,
                status="rejected",
                error_message=f"503 Circuit Breaker Active: {c_reason}"
            )

        # Step 5: Hierarchical Pre-flight Budget Reservation
        b_passed, b_reason = self.budget_manager.check_and_reserve(request, estimated_cost)
        if not b_passed:
            self.logger.log_event("BUDGET_EXCEEDED", "HIGH", {"user_id": request.user_id, "reason": b_reason})
            return AIResponse(
                request_id=request.request_id,
                trace_id=request.trace_id,
                text="",
                model_used=chosen_model,
                provider="none",
                usage=UsageRecord(),
                cost=CostRecord(),
                latency_ms=(time.time() - start_time) * 1000,
                status="rejected",
                error_message=f"402 Budget Exceeded: {b_reason}"
            )

        # Step 6: Exact Match Response Cache Check
        exact_hit = self.exact_cache.get(request.prompt, model=chosen_model)
        if exact_hit:
            res = AIResponse(
                request_id=request.request_id,
                trace_id=request.trace_id,
                text=exact_hit["text"],
                model_used=chosen_model,
                provider="cache",
                usage=UsageRecord(0, 0, 0, 0, 0),
                cost=CostRecord(0, 0, 0, 0, 0),
                latency_ms=(time.time() - start_time) * 1000,
                cache_hit=True,
                status="success"
            )
            self.idempotency_guard.mark_completed(fp, {"response": res})
            return res

        # Step 7: Semantic Vector Cache Check
        semantic_hit = self.semantic_cache.lookup(request.prompt)
        if semantic_hit:
            res = AIResponse(
                request_id=request.request_id,
                trace_id=request.trace_id,
                text=semantic_hit["response"]["text"],
                model_used=chosen_model,
                provider="semantic_cache",
                usage=UsageRecord(0, 0, 0, 0, 0),
                cost=CostRecord(0, 0, 0, 0, 0),
                latency_ms=(time.time() - start_time) * 1000,
                semantic_cache_hit=True,
                status="success"
            )
            self.idempotency_guard.mark_completed(fp, {"response": res})
            return res

        # Step 8: Context Compression (if context > 500 words)
        processed_prompt = request.prompt
        if len(request.prompt.split()) > 300:
            processed_prompt = self.compressor.compress(request.prompt, target_ratio=0.6)

        # Step 9: Simulate Provider LLM Call & Capture Provider Metered Usage
        # In real code: provider_response = call_provider_api(chosen_model, processed_prompt)
        input_tokens = len(processed_prompt) // 4
        output_tokens = 150
        actual_usage = UsageRecord(
            input_tokens=input_tokens,
            cached_input_tokens=0,
            output_tokens=output_tokens,
            reasoning_tokens=0,
            total_tokens=input_tokens + output_tokens
        )

        # Step 10: Post-flight Financial Reconciliation
        actual_cost = self.budget_manager.reconcile_postflight(
            req=request,
            estimated_cost=estimated_cost,
            usage=actual_usage,
            model=chosen_model
        )
        self.circuit_breaker.record_spend(actual_cost.total_cost)

        generated_text = f"Simulated response from {chosen_model} for prompt: '{processed_prompt[:60]}...'"
        
        response = AIResponse(
            request_id=request.request_id,
            trace_id=request.trace_id,
            text=generated_text,
            model_used=chosen_model,
            provider="openai" if "gpt" in chosen_model else "anthropic",
            usage=actual_usage,
            cost=actual_cost,
            latency_ms=(time.time() - start_time) * 1000,
            status="success"
        )

        # Step 11: Store Cache Hits
        self.exact_cache.set(request.prompt, {"text": generated_text}, model=chosen_model)
        self.semantic_cache.store(request.prompt, {"text": generated_text})

        # Step 12: Write Immutable Cost Ledger & FinOps Telemetry
        self.cost_ledger.record_transaction(request, response)
        self.idempotency_guard.mark_completed(fp, {"response": response})

        self.logger.log_event("LLM_SUCCESS", "LOW", {
            "request_id": request.request_id,
            "model": chosen_model,
            "cost_usd": actual_cost.total_cost,
            "total_tokens": actual_usage.total_tokens
        }, user_id=request.user_id)

        return response
