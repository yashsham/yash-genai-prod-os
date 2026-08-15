from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import time
import uuid

@dataclass
class AIRequest:
    """
    Standardized request wrapper for all LLM calls.
    Enforces user, tenant, feature identification and budget limits.
    """
    prompt: str
    user_id: str
    tenant_id: str
    feature_id: str
    task_type: str = "general" # classification, summarization, extraction, reasoning, agent
    context: Optional[str] = None
    messages: List[Dict[str, str]] = field(default_factory=list)
    preferred_model: Optional[str] = None
    max_tokens: Optional[int] = 2048
    max_cost_usd: Optional[float] = 0.10
    idempotency_key: Optional[str] = None
    request_id: str = field(default_factory=lambda: f"req_{uuid.uuid4().hex[:12]}")
    trace_id: str = field(default_factory=lambda: f"trace_{uuid.uuid4().hex[:16]}")
    created_at: float = field(default_factory=time.time)

@dataclass
class UsageRecord:
    """
    Tracks precise token consumption including cached and reasoning tokens.
    """
    input_tokens: int = 0
    cached_input_tokens: int = 0
    output_tokens: int = 0
    reasoning_tokens: int = 0
    total_tokens: int = 0

@dataclass
class CostRecord:
    """
    Monetary financial accounting breakdown per request.
    """
    input_cost: float = 0.0
    cached_input_cost: float = 0.0
    output_cost: float = 0.0
    reasoning_cost: float = 0.0
    tool_cost: float = 0.0
    total_cost: float = 0.0
    currency: str = "USD"

@dataclass
class AIResponse:
    """
    Standardized response returned by AIControl plane.
    Includes financial telemetry, latency, cache hits, and execution metadata.
    """
    request_id: str
    trace_id: str
    text: str
    model_used: str
    provider: str
    usage: UsageRecord
    cost: CostRecord
    latency_ms: float
    cache_hit: bool = False
    semantic_cache_hit: bool = False
    status: str = "success" # success, degraded, rejected
    error_message: Optional[str] = None
