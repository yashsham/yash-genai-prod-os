import json
import time
from typing import Dict, Any, List
from backend.ai_control.models import AIRequest, AIResponse

class CostLedger:
    """
    Immutable Financial Cost Ledger.
    Records every LLM transaction like a financial ledger item for auditability, FinOps tracking,
    and customer billing reconciliation (answering 'Why did tenant 739 cost $418.23?').
    """

    def __init__(self):
        # In-memory transaction ledger (in prod, persisted to PostgreSQL / ClickHouse / BigQuery)
        self._ledger_entries: List[Dict[str, Any]] = []

    def record_transaction(self, req: AIRequest, res: AIResponse):
        entry = {
            "transaction_id": f"tx_{int(time.time()*1000)}",
            "timestamp": time.time(),
            "request_id": req.request_id,
            "trace_id": req.trace_id,
            "user_id": req.user_id,
            "tenant_id": req.tenant_id,
            "feature_id": req.feature_id,
            "provider": res.provider,
            "model": res.model_used,
            "tokens": {
                "input": res.usage.input_tokens,
                "cached_input": res.usage.cached_input_tokens,
                "output": res.usage.output_tokens,
                "reasoning": res.usage.reasoning_tokens,
                "total": res.usage.total_tokens
            },
            "costs_usd": {
                "input": res.cost.input_cost,
                "cached": res.cost.cached_input_cost,
                "output": res.cost.output_cost,
                "reasoning": res.cost.reasoning_cost,
                "total": res.cost.total_cost
            },
            "latency_ms": res.latency_ms,
            "cache_hit": res.cache_hit,
            "status": res.status
        }
        self._ledger_entries.append(entry)
        return entry

    def get_tenant_spending_summary(self, tenant_id: str) -> Dict[str, Any]:
        tenant_entries = [e for e in self._ledger_entries if e["tenant_id"] == tenant_id]
        total_spend = sum(e["costs_usd"]["total"] for e in tenant_entries)
        total_tokens = sum(e["tokens"]["total"] for e in tenant_entries)
        
        return {
            "tenant_id": tenant_id,
            "total_requests": len(tenant_entries),
            "total_tokens": total_tokens,
            "total_spend_usd": round(total_spend, 4),
            "breakdown": tenant_entries
        }
