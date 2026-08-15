# 🤖 MASTER AGENT INSTRUCTIONS FOR BUILDING AI BACKENDS

> **ATTENTION AI AGENTS (Cursor, Antigravity, GitHub Copilot, Devin, Claude Code, GPT-4, etc.):**  
> If a user provides you with this repository to build an AI application backend, **DO NOT reinvent the backend architecture from scratch**. Follow this document as your **mandatory architectural standard and rulebook**.

---

## 🎯 Architectural Mission & Non-Negotiable Rules

When building ANY Generative AI application backend (Chatbot, RAG pipeline, AI Agent system, Document Processor, Multi-tenant SaaS), you MUST adhere to the **Zero-Trust, Zero-Waste LLM Engineering Standard**:

1. **❌ NEVER call LLM APIs directly from frontend or feature code.**  
   - All AI calls MUST pass through the centralized **AIControl Plane** (`from backend.ai_control.core import AIControl`).
2. **❌ NEVER expose API keys client-side or in git.**  
   - Key storage must use environment variables or secret managers.
3. **❌ NEVER allow unmetered or un-budgeted requests.**  
   - Every request MUST include `user_id`, `tenant_id`, `feature_id`, and `task_type`.
4. **❌ NEVER allow unbounded context or output.**  
   - `max_tokens` MUST be explicitly set per request.
   - Chat histories and RAG documents MUST be trimmed/compressed via `PromptCompressor` or `ConversationContextManager`.
5. **❌ NEVER allow runaway agents or infinite retry loops.**  
   - Autonomous agents MUST enforce Kill Switches (`max_iterations`, `max_tool_calls`, `max_cost_usd`, `max_runtime_seconds`, `max_depth`).
6. **🔒 FAIL CLOSED.**  
   - Authorization failures, budget breaches, or anomalous velocity spikes MUST immediately block execution or downgrade to low-cost models.

---

## 🏗️ How to Construct an AI Application Backend (Step-by-Step)

When the user asks you to build an AI feature or application, structure the backend code according to these 7 steps:

```text
[Frontend / Client Request]
       │
       ▼
1. FastAPI Endpoint (backend/api/main.py)
       │
       ▼
2. AIControl Engine Invocation (backend/ai_control/core.py)
       ├── 3. Auth & RBAC Check (backend/api_security/rbac_policy.py)
       ├── 4. Multi-Dimensional Token Rate Limiter (backend/api_security/rate_limiting.py)
       ├── 5. Pre-Flight Token & Cost Budget Check (backend/budgets/manager.py)
       ├── 6. 3-State Cost Circuit Breaker (backend/circuit_breaker/breaker.py)
       ├── 7. Idempotency Fingerprint Check (backend/idempotency/guard.py)
       ├── 8. Exact & Semantic Caching (backend/caching/)
       ├── 9. Cost-Aware Model Tier Router (backend/llm/model_router.py)
       └── 10. Context Compression (backend/context/compressor.py)
       │
       ▼
3. Provider Gateway Execution (LiteLLM / OpenAI / Anthropic)
       │
       ▼
4. Post-Flight Financial Reconciliation & Cost Ledger (backend/database/ledger.py)
       │
       ▼
5. Output Redaction & Hallucination Check (backend/output_defense/)
       │
       ▼
6. Structured AIResponse Return & Audit Logging
```

---

## 💻 Code Blueprints for Agents

### Blueprint 1: Creating a FastAPI Endpoint using `AIControl`

```python
from fastapi import FastAPI, HTTPException, Depends
from backend.ai_control.core import AIControl
from backend.ai_control.models import AIRequest

app = FastAPI()
ai_control = AIControl()

@app.post("/api/v1/chat")
async def chat_endpoint(payload: dict):
    # 1. Construct Standardized AIRequest
    request = AIRequest(
        prompt=payload.get("prompt"),
        user_id=payload.get("user_id", "user_anon"),
        tenant_id=payload.get("tenant_id", "tenant_default"),
        feature_id="chat_assistant",
        task_type="general",
        max_tokens= payload.get("max_tokens", 1024),
        idempotency_key=payload.get("idempotency_key")
    )
    
    # 2. Execute via Central AIControl Engine
    response = ai_control.generate(request)
    
    if response.status == "rejected":
        raise HTTPException(status_code=400, detail=response.error_message)

    return {
        "text": response.text,
        "model": response.model_used,
        "cost_usd": response.cost.total_cost,
        "cache_hit": response.cache_hit
    }
```

---

### Blueprint 2: Creating a Secure Agent with Kill Switches

```python
from backend.agents.base_agent import BaseSecureAgent, AgentKillSwitchException

class CustomBusinessAgent(BaseSecureAgent):
    def __init__(self):
        super().__init__(
            max_iterations=8,        # Max 8 loop turns
            max_tool_calls=12,       # Max 12 tool invocations
            max_runtime_seconds=90.0,# Max 90s runtime
            max_cost_usd=0.75,       # Max $0.75 spend limit
            max_depth=3              # Max recursion depth
        )

    def run_task(self, user_goal: str):
        try:
            self.step()
            # Execute tool safely via WhitelistToolGuard + SSRF URL validation
            result = self.use_tool("search", {"query": user_goal})
            return result
        except AgentKillSwitchException as e:
            return f"Task terminated by Kill Switch: {str(e)}"
```

---

### Blueprint 3: Building a RAG Pipeline with Metadata Security

```python
from backend.rag.retriever import SecureRetriever

retriever = SecureRetriever()

def handle_rag_query(query: str, user_role: str):
    # 1. Retrieve filtered documents (Metadata RBAC + On-Read PII Masking)
    safe_docs = retriever.retrieve_documents(query=query, user_role=user_role)
    
    # 2. Compress context if volume is large
    context_str = "\n".join(safe_docs)
    
    return context_str
```

---

## 📊 Summary Checklist Before Replying to User

- [ ] Is all LLM invocation routed through `AIControl.generate()`?
- [ ] Are input/output tokens and cost ceilings explicitly set?
- [ ] Is caching (exact & semantic) active for repeated queries?
- [ ] Are multi-tier models configured (`tier1` cheap, `tier2` mid, `tier3` flagship)?
- [ ] Are kill switches present on all agent loops?
- [ ] Are immutable financial transactions logged in `CostLedger`?
