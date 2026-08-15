from typing import Any, Dict, Optional
import time
from collections import defaultdict

from backend.agent_security.sandbox import SubprocessMockSandbox
from backend.agent_security.tool_guard import WhitelistToolGuard

class AgentKillSwitchException(Exception):
    """Raised when an agent violates execution boundaries or enters an infinite loop."""
    pass

class AgentDepthExceededException(Exception):
    """Raised when recursive inter-agent call depth exceeds safety limit."""
    pass

class BaseSecureAgent:
    """
    Production-Grade Secure Agent runtime with strict Kill Switches & Execution Boundaries:
    - max_iterations (default: 8)
    - max_tool_calls (default: 12)
    - max_runtime_seconds (default: 90s)
    - max_cost_usd (default: $0.75)
    - max_depth (default: 3)
    
    Prevents quadratic cost escalation, infinite planning loops, and runaway background jobs.
    """

    def __init__(
        self,
        max_iterations: int = 8,
        max_tool_calls: int = 12,
        max_runtime_seconds: float = 90.0,
        max_cost_usd: float = 0.75,
        max_depth: int = 3
    ):
        self.max_iterations = max_iterations
        self.max_tool_calls = max_tool_calls
        self.max_runtime_seconds = max_runtime_seconds
        self.max_cost_usd = max_cost_usd
        self.max_depth = max_depth

        self.sandbox = SubprocessMockSandbox()
        self.tool_guard = WhitelistToolGuard()

        # Session tracking state
        self.iteration_count = 0
        self.tool_call_count = 0
        self.start_time = time.time()
        self.accumulated_cost = 0.0

    def check_kill_switches(self, current_depth: int = 1):
        """
        Enforces execution boundaries before every LLM turn or tool invocation.
        """
        # 1. Depth Check
        if current_depth > self.max_depth:
            raise AgentDepthExceededException(f"Agent recursion depth ({current_depth}) exceeded limit ({self.max_depth})")

        # 2. Iteration Check
        if self.iteration_count >= self.max_iterations:
            raise AgentKillSwitchException(f"Agent iteration limit reached ({self.iteration_count}/{self.max_iterations})")

        # 3. Tool Call Check
        if self.tool_call_count >= self.max_tool_calls:
            raise AgentKillSwitchException(f"Agent tool call limit reached ({self.tool_call_count}/{self.max_tool_calls})")

        # 4. Wall-Clock Timeout Check
        elapsed = time.time() - self.start_time
        if elapsed > self.max_runtime_seconds:
            raise AgentKillSwitchException(f"Agent runtime timeout ({elapsed:.1f}s > {self.max_runtime_seconds}s)")

        # 5. Financial Cost Limit Check
        if self.accumulated_cost >= self.max_cost_usd:
            raise AgentKillSwitchException(f"Agent financial limit reached (${self.accumulated_cost:.2f} >= ${self.max_cost_usd:.2f})")

    def use_tool(self, tool_name: str, args: Dict[str, Any], current_depth: int = 1) -> Any:
        """
        Securely checks kill switches, validates tool permissions, and executes tool call.
        """
        self.check_kill_switches(current_depth)
        
        if not self.tool_guard.validate_tool_call(tool_name, args):
            self.tool_guard.record_tool_result(tool_name, success=False)
            raise PermissionError(f"Tool execution denied: {tool_name}")

        self.tool_call_count += 1
        print(f"Agent executing tool '{tool_name}' (Call {self.tool_call_count}/{self.max_tool_calls})")
        
        # Simulate execution
        self.tool_guard.record_tool_result(tool_name, success=True)
        return f"Result from {tool_name}"

    def step(self, current_depth: int = 1):
        """
        Advances agent execution turn while incrementing iteration counters.
        """
        self.check_kill_switches(current_depth)
        self.iteration_count += 1
        print(f"Agent step {self.iteration_count}/{self.max_iterations}")
