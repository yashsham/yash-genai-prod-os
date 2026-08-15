from dataclasses import dataclass
from typing import Optional
import time

@dataclass
class AIRequestTable:
    id: Optional[int]
    request_id: str
    trace_id: str
    user_id: str
    tenant_id: str
    feature_id: str
    provider: str
    model: str
    status: str
    created_at: float
    latency_ms: float

@dataclass
class AIUsageTable:
    request_id: str
    input_tokens: int
    cached_input_tokens: int
    output_tokens: int
    reasoning_tokens: int
    total_tokens: int

@dataclass
class AICostTable:
    request_id: str
    input_cost: float
    cached_cost: float
    output_cost: float
    tool_cost: float
    total_cost: float
    currency: str

@dataclass
class AIBudgetTable:
    scope_type: str # global, tenant, user, feature
    scope_id: str
    daily_limit: float
    monthly_limit: float
    current_daily_spend: float
    current_monthly_spend: float

@dataclass
class AIModelPriceTable:
    provider: str
    model: str
    input_price_per_m: float
    cached_input_price_per_m: float
    output_price_per_m: float
    effective_from: str
