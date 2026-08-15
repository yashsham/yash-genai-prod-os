## 🤖 Agent Design Principles & Governance Rules

- **One agent = one job**  
  Each agent must have a single, well-defined responsibility to avoid uncontrolled behavior.

- **No self-modifying logic**  
  Agents must not alter their own code, prompts, or permissions at runtime.

- **Tool access via allow-list**  
  Agents can only invoke explicitly approved tools verified by `WhitelistToolGuard`. No dynamic or unrestricted tool access is allowed.

- **Strict Kill Switches Enforced**  
  Every autonomous agent MUST enforce execution boundaries:
  - `max_iterations`: 8 turns max
  - `max_tool_calls`: 12 calls max
  - `max_runtime_seconds`: 90 seconds max
  - `max_cost_usd`: $0.75 max
  - `max_depth`: 3 recursion levels max (raises `AgentDepthExceededException`)

- **Tool Failure Circuit Breaker**  
  Trips after 3 consecutive tool failures (`max_consecutive_failures = 3`).

- **MCP & SSRF Endpoint Defense**  
  All tool URL calls must validate against `validate_url_safety()` to block loopback interfaces, RFC1918 private IPs, and cloud metadata endpoints.
