from abc import ABC, abstractmethod
from typing import List

class DLPScanner(ABC):
    """
    Data Loss Prevention (DLP) Scanner Interface.
    Scans data streams or files for sensitive information leakage.
    """

    @abstractmethod
    def scan_content(self, content: str, context: str = None) -> bool:
        """
        Checks if content violates DLP policies.
        params:
            content: The text/data to check
            context: Optional context (e.g., 'public_response', 'internal_log')
        returns:
            True if violation detected, False otherwise
        """
        pass

    @abstractmethod
    def get_violation_report(self) -> dict:
        """
        Returns details of the last violation.
        """
        pass

class KeywordDLPScanner(DLPScanner):
    """
    Simple DLP scanner that looks for 'CONFIDENTIAL' or 'INTERNAL' markers.
    """

    SENSITIVE_KEYWORDS = ["CONFIDENTIAL", "INTERNAL USE ONLY", "SECRET_KEY"]

    def __init__(self):
        self.last_violation = None

    def scan_content(self, content: str, context: str = None) -> bool:
        self.last_violation = None
        for keyword in self.SENSITIVE_KEYWORDS:
            if keyword in content:
                self.last_violation = {
                    "keyword": keyword,
                    "context": context,
                    "timestamp": "now"
                }
                return True
        return False

    def get_violation_report(self) -> dict:
        return self.last_violation
