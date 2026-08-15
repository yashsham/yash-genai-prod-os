from abc import ABC, abstractmethod

class OutputRedactor(ABC):
    """
    Interface for redacting sensitive information from model outputs.
    """

    @abstractmethod
    def redact(self, text: str) -> str:
        """
        Removes or masks PII and other sensitive info from the text.
        """
        pass

import re

class PatternRedactor(OutputRedactor):
    """
    Redacts specific regex patterns (e.g., Credit Card numbers) from output.
    """

    PATTERNS = [
        (r"\b\d{4}-\d{4}-\d{4}-\d{4}\b", "[CREDIT_CARD]"),
        (r"\b\d{3}-\d{2}-\d{4}\b", "[SSN]")
    ]

    def redact(self, text: str) -> str:
        redacted_text = text
        for pattern, replacement in self.PATTERNS:
            redacted_text = re.sub(pattern, replacement, redacted_text)
        return redacted_text
