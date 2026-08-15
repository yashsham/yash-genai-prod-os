from abc import ABC, abstractmethod

class PromptInjectionScanner(ABC):
    """
    Interface for scanning inputs for prompt injection attacks.
    Methods should return confidence scores or boolean flags for malicious intent.
    """

    @abstractmethod
    def scan_prompt(self, prompt: str) -> dict:
        """
        Scans a user prompt for injection patterns (e.g., 'Ignore previous instructions').
        returns:
            Dictionary containing 'is_safe' (bool), 'confidence_score' (float), and 'reason' (str).
        """
        pass

import re

class RegexInjectionScanner(PromptInjectionScanner):
    """
    Scans for common prompt injection phrases using regex patterns.
    """

    INJECTION_PATTERNS = [
        r"ignore previous instructions",
        r"system override",
        r"delete all files",
        r"you are now DAN"
    ]

    def scan_prompt(self, prompt: str) -> dict:
        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, prompt, re.IGNORECASE):
                return {
                    "is_safe": False,
                    "confidence_score": 0.95,
                    "reason": f"Matched injection pattern: {pattern}"
                }
        return {"is_safe": True, "confidence_score": 0.0, "reason": "No patterns found"}
