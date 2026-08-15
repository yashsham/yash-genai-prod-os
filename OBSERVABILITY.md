## Mandatory Observability Logs

The following signals must be logged for every GenAI request without exception:

- **Prompt hash**  
  Store a cryptographic hash of the prompt to enable auditability without exposing raw user input.

- **Tool calls**  
  Log all tool invocations, including tool name, parameters (sanitized), and execution outcome.

- **Token usage**  
  Track prompt tokens, completion tokens, and total token consumption per request.

- **Latency**  
  Measure and log end-to-end latency as well as per-stage latency (retrieval, inference, tool execution).

- **Security violations**  
  Record all detected policy breaches, prompt injection attempts, and access control failures.
