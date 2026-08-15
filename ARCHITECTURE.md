## System Architecture (Zero-Trust GenAI)

```text
Frontend (Zero Trust)
 ├─ Input Sanitization
 ├─ Client-side Encryption
 └─ Rate Limiting
      ↓
API Gateway / WAF
      ↓
Auth Service (JWT / OAuth)
      ↓
Prompt Firewall
      ↓
Agent Orchestrator
      ↓
Tool Sandbox
      ↓
LLM
      ↓
Output Filter & Redaction
      ↓
Audit Logs + Metrics

