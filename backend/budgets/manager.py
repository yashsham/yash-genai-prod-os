from typing import Dict, Any, Tuple
import time
from collections import defaultdict
from backend.ai_control.models import AIRequest, CostRecord, UsageRecord

class BudgetManager:
    """
    Hierarchical Token & Spend Governance Engine.
    Enforces multi-level spend caps: Global, Tenant, User, Feature, and Per-Request.
    Provides pre-flight budget reservation and post-flight actual reconciliation.
    """
    
    # Model pricing per 1M tokens (USD)
    MODEL_PRICING = {
        "gpt-4o-mini": {"input": 0.15, "cached": 0.075, "output": 0.60},
        "gpt-4o": {"input": 2.50, "cached": 1.25, "output": 10.00},
        "claude-3-5-haiku": {"input": 0.80, "cached": 0.08, "output": 4.00},
        "claude-3-5-sonnet": {"input": 3.00, "cached": 0.30, "output": 15.00},
        "default": {"input": 1.00, "cached": 0.50, "output": 5.00}
    }

    def __init__(self):
        # Budget ceilings (USD)
        self.global_daily_limit = 100.00
        self.tenant_daily_limit = 20.00
        self.user_daily_limit = 2.00
        self.request_max_cost_limit = 0.10
        
        # Real-time spend trackers (in-memory mock; in prod uses Redis atomic counters)
        self.global_daily_spend = 0.0
        self.tenant_daily_spend = defaultdict(float)
        self.user_daily_spend = defaultdict(float)
        self.feature_daily_spend = defaultdict(float)

    def estimate_preflight_cost(self, prompt: str, context: str = None, model: str = "gpt-4o-mini", max_output_tokens: int = 1024) -> float:
        """
        Estimates maximum possible request cost BEFORE sending payload to provider.
        Formula: (estimated_input_tokens * input_price + max_output_tokens * output_price) / 1,000,000
        """
        pricing = self.MODEL_PRICING.get(model, self.MODEL_PRICING["default"])
        # Crude token estimation (~4 chars/token)
        input_tokens = len(prompt) // 4 + (len(context) // 4 if context else 0) + 100 # buffer
        
        estimated_cost = (
            (input_tokens * pricing["input"]) +
            (max_output_tokens * pricing["output"])
        ) / 1_000_000.0
        
        return round(estimated_cost, 6)

    def check_and_reserve(self, req: AIRequest, estimated_cost: float) -> Tuple[bool, str]:
        """
        Checks if estimated request cost violates any budget ceiling.
        Returns (allowed: bool, reason: str).
        """
        # 1. Single Request Ceiling
        if estimated_cost > self.request_max_cost_limit:
            return False, f"Request estimated cost (${estimated_cost:.4f}) exceeds per-request limit (${self.request_max_cost_limit:.2f})"

        # 2. User Daily Ceiling
        if self.user_daily_spend[req.user_id] + estimated_cost > self.user_daily_limit:
            return False, f"User '{req.user_id}' daily budget limit reached (${self.user_daily_limit:.2f})"

        # 3. Tenant Daily Ceiling
        if self.tenant_daily_spend[req.tenant_id] + estimated_cost > self.tenant_daily_limit:
            return False, f"Tenant '{req.tenant_id}' daily budget limit reached (${self.tenant_daily_limit:.2f})"

        # 4. Global Daily Ceiling
        if self.global_daily_spend + estimated_cost > self.global_daily_limit:
            return False, f"Global system daily budget limit reached (${self.global_daily_limit:.2f})"

        # Reserve spend tentatively
        self.global_daily_spend += estimated_cost
        self.tenant_daily_spend[req.tenant_id] += estimated_cost
        self.user_daily_spend[req.user_id] += estimated_cost
        self.feature_daily_spend[req.feature_id] += estimated_cost

        return True, "Pre-flight budget check passed"

    def reconcile_postflight(self, req: AIRequest, estimated_cost: float, usage: UsageRecord, model: str) -> CostRecord:
        """
        Reconciles actual provider token usage against pre-flight reservation.
        Updates spend ledgers with exact calculated cost.
        """
        pricing = self.MODEL_PRICING.get(model, self.MODEL_PRICING["default"])
        
        actual_input_cost = (usage.input_tokens * pricing["input"]) / 1_000_000.0
        actual_cached_cost = (usage.cached_input_tokens * pricing["cached"]) / 1_000_000.0
        actual_output_cost = (usage.output_tokens * pricing["output"]) / 1_000_000.0
        actual_reasoning_cost = (usage.reasoning_tokens * pricing["output"]) / 1_000_000.0
        
        actual_total_cost = round(actual_input_cost + actual_cached_cost + actual_output_cost + actual_reasoning_cost, 6)
        
        # Adjust ledger variance (diff between estimated reservation and actual charge)
        variance = actual_total_cost - estimated_cost
        self.global_daily_spend += variance
        self.tenant_daily_spend[req.tenant_id] += variance
        self.user_daily_spend[req.user_id] += variance
        self.feature_daily_spend[req.feature_id] += variance

        return CostRecord(
            input_cost=round(actual_input_cost, 6),
            cached_input_cost=round(actual_cached_cost, 6),
            output_cost=round(actual_output_cost, 6),
            reasoning_cost=round(actual_reasoning_cost, 6),
            total_cost=actual_total_cost,
            currency="USD"
        )
