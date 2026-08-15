# 📋 Master Production Launch Checklist

- [ ] API keys stored server-side only in secret manager (never client bundle or git).
- [ ] Every AI endpoint behind auth + per-user/tenant rate limit.
- [ ] Multi-dimensional token rate limiting enforced (RPM, TPM, ITPM, OTPM, Concurrency).
- [ ] Pre-flight token counting & cost estimation before every call.
- [ ] Hierarchical budget ceilings defined & enforced (Global, Tenant, User, Feature, Request).
- [ ] 3-State Cost Circuit Breaker active (CLOSED → HALF_OPEN @ 80% → OPEN @ 100%).
- [ ] Spend velocity tripwires monitored (< $5/min velocity).
- [ ] `max_tokens` explicitly set on every request.
- [ ] Exact-match and semantic vector caching (Tau >= 0.94) enabled.
- [ ] Provider prompt-caching used for static system prompts & docs.
- [ ] Cost-aware multi-tier model router active (Tier 1 cheap, Tier 2 mid, Tier 3 flagship).
- [ ] Context window trimming & LLMLingua-2 prompt compression configured.
- [ ] Agent Kill Switches enforced (`max_iterations`, `max_tool_calls`, `max_runtime`, `max_cost`, `max_depth`).
- [ ] Tool failure circuit breakers ($K \ge 3$) and SSRF URL validation active.
- [ ] Idempotency keys & request fingerprinting active on user actions.
- [ ] Real-time cost logging & immutable `CostLedger` transactions recorded.
- [ ] Prompt injection defenses & output redaction verified.
- [ ] Load tests prove budget controls stop runaway bills.
