from abc import ABC, abstractmethod

class ContentFilter(ABC):
    """
    Abstract base class for content filtering (Hate, Violence, Self-Harm).
    """

    @abstractmethod
    def check_content(self, text: str) -> dict:
        """
        Checks text against safety guidelines.
        returns:
            Dict with 'blocked' (bool), 'categories' (list of violated categories).
        """
        pass

class KeywordContentFilter(ContentFilter):
    """
    Blocks content containing specific banned words.
    """
    
    BANNED_WORDS = {
        "violence": ["kill", "murder", "attack"],
        "PII": ["ssn", "credit card"] 
    }

    def check_content(self, text: str) -> dict:
        violations = []
        lower_text = text.lower()
        for category, words in self.BANNED_WORDS.items():
            for word in words:
                if word in lower_text:
                    violations.append(category)
                    break 
        
        if violations:
            return {"blocked": True, "categories": violations}
        return {"blocked": False, "categories": []}
