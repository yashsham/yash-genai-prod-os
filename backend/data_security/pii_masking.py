from abc import ABC, abstractmethod
from typing import List, Dict, Any

class PIIMaskingStrategy(ABC):
    """
    Abstract base class for PII masking strategies.
    Ensures consistent interface for different masking implementations (e.g., Presidio, Regex).
    """
    
    @abstractmethod
    def scan(self, text: str) -> List[Dict[str, Any]]:
        """
        Scans text for PII entities.
        params:
            text: Input text string
        returns:
             List of detected PII entities with metadata (type, confidence, start/end)
        """
        pass

    @abstractmethod
    def mask(self, text: str, entities: List[Dict[str, Any]]) -> str:
        """
        Masks detected PII in the text.
        params:
            text: Original text
            entities: List of entities to mask
        returns:
            Sanitized text string
        """
        pass

import re

class RegexPIIMaskingStrategy(PIIMaskingStrategy):
    """
    Demo implementation using simple Regex for email and phone numbers.
    """
    
    PATTERNS = {
        "EMAIL": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "PHONE": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"
    }

    def scan(self, text: str) -> List[Dict[str, Any]]:
        findings = []
        for p_type, pattern in self.PATTERNS.items():
            for match in re.finditer(pattern, text):
                findings.append({
                    "type": p_type,
                    "start": match.start(),
                    "end": match.end(),
                    "text": match.group()
                })
        return findings

    def mask(self, text: str, entities: List[Dict[str, Any]]) -> str:
        # Sort entities by start index in reverse to avoid offset issues
        sorted_entities = sorted(entities, key=lambda x: x["start"], reverse=True)
        masked_text = text
        for entity in sorted_entities:
            masked_text = masked_text[:entity["start"]] + f"<{entity['type']}>" + masked_text[entity["end"]:]
        return masked_text
