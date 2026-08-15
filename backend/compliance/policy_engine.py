from abc import ABC, abstractmethod
from typing import List

class PolicyEngine(ABC):
    """
    Central engine for enforcing compliance policies (GDPR, Internal Policy).
    """

    @abstractmethod
    def enforce_policies(self, data: dict, policy_tags: List[str]) -> dict:
        """
        Applies policy rules to the data.
        e.g., checks data retention rules, consent flags.
        returns:
            Compliant data object (potentially modified) or raises PolicyViolationException.
        """
        pass

class SimplePolicyEngine(PolicyEngine):
    """
    Enforces basic GDPR-like checks.
    """

    def enforce_policies(self, data: dict, policy_tags: List[str]) -> dict:
        if "GDPR" in policy_tags:
            # Enforce user consent present
            if not data.get("user_consent", False):
                raise ValueError("Policy Violation: Missing User Consent for GDPR data processing.")
                
            # Simulate removing fields not allowed for storage
            if "biometric_data" in data:
                del data["biometric_data"] # Minimize data
                
        return data
