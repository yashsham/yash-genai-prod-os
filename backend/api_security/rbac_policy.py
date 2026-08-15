from typing import List, Dict

class RBACPolicy:
    """
    Definition of Role-Based Access Control logic.
    """
    
    def __init__(self, roles: Dict[str, List[str]]):
        self.roles = roles  # e.g., {'admin': ['*'], 'viewer': ['read']}

    def has_permission(self, role: str, action: str) -> bool:
        """
        Checks if the role permits the action.
        """
        if role not in self.roles:
            return False
        permissions = self.roles[role]
        return '*' in permissions or action in permissions
