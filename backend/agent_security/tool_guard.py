from abc import ABC, abstractmethod
from typing import Dict, Any, List
import re
import urllib.parse

class ToolGuard(ABC):
    @abstractmethod
    def validate_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> bool:
        pass

class WhitelistToolGuard(ToolGuard):
    """
    Interception layer for Agent Tool calls.
    Enforces tool allowlists, argument sanitization, MCP URL validation (SSRF defense),
    and consecutive tool failure circuit breakers.
    """

    ALLOWED_TOOLS = ["calculator", "search", "weather", "read_db", "generate_report"]
    
    # Private IP and Cloud Metadata SSRF blocklist (RFC1918 + Link Local)
    BLOCKED_HOST_PATTERNS = [
        r"^127\.", r"^localhost", r"^169\.254\.", r"^10\.", 
        r"^172\.(1[6-9]|2[0-9]|3[01])\.", r"^192\.168\."
    ]

    def __init__(self, max_consecutive_failures: int = 3):
        self.max_consecutive_failures = max_consecutive_failures
        self.failure_counters = defaultdict(int)

    def validate_url_safety(self, url: str) -> bool:
        """
        SSRF Defense: Validates URLs invoked by MCP tools.
        Blocks loopbacks, private IPs, and metadata endpoints.
        """
        try:
            parsed = urllib.parse.urlparse(url)
            hostname = parsed.hostname or ""
            for pattern in self.BLOCKED_HOST_PATTERNS:
                if re.search(pattern, hostname, re.IGNORECASE):
                    print(f"ToolGuard SSRF Defense: Blocked private/metadata host '{hostname}'")
                    return False
            return True
        except Exception:
            return False

    def validate_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> bool:
        # 1. Allowlist Check
        if tool_name not in self.ALLOWED_TOOLS:
            print(f"ToolGuard: Blocked unauthorized tool '{tool_name}'")
            return False

        # 2. Failure Circuit Breaker Check
        if self.failure_counters[tool_name] >= self.max_consecutive_failures:
            print(f"ToolGuard: Circuit Breaker TRIPPED for tool '{tool_name}' ({self.failure_counters[tool_name]} consecutive failures)")
            return False

        # 3. URL Parameter Check
        if "url" in arguments:
            if not self.validate_url_safety(str(arguments["url"])):
                return False

        return True

    def record_tool_result(self, tool_name: str, success: bool):
        """
        Tracks tool invocation outcomes to trip tool circuit breakers on repeated failures.
        """
        if success:
            self.failure_counters[tool_name] = 0
        else:
            self.failure_counters[tool_name] += 1
