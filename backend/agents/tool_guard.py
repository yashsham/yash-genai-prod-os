from typing import Dict, Any, List
import yaml
import os

# Delegation to the core Security Framework
from backend.agent_security.tool_guard import WhitelistToolGuard

class AgentToolGuard:
    """
    Local wrapper for the Agent service that checks permissions against permissions.yaml
    and strictly enforces tool whitelisting via the Security Framework.
    """

    def __init__(self, permissions_file: str = "backend/agents/permissions.yaml"):
        self.security_guard = WhitelistToolGuard()
        self.permissions = self._load_permissions(permissions_file)

    def _load_permissions(self, path: str) -> Dict:
        # Mock loading if file doesn't technically exist in runtime path context
        if not os.path.exists(path):
            return {"roles": {"default": {"permissions": []}}}
        
        with open(path, 'r') as f:
            return yaml.safe_load(f)

    def validate_tool_usage(self, agent_role: str, tool_name: str, args: Dict[str, Any]) -> bool:
        # 1. Check Framework Guard (Security Layer)
        if not self.security_guard.validate_tool_call(tool_name, args):
            return False

        # 2. Check Business Logic Permissions (Agent Layer)
        role_config = self.permissions.get("roles", {}).get(agent_role, {})
        allowed_tools = role_config.get("permissions", [])
        
        if "*" in allowed_tools:
            return True
            
        return f"tool:{tool_name}" in allowed_tools
