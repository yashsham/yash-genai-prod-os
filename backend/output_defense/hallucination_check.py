from abc import ABC, abstractmethod

class HallucinationChecker(ABC):
    """
    Interface for verifying the factual consistency of model outputs.
    """

    @abstractmethod
    def check_consistency(self, generated_text: str, source_documents: list) -> float:
        """
        Returns a confidence score (0.0 - 1.0) indicating factual consistency with sources.
        """
        pass

class NgramOverlapChecker(HallucinationChecker):
    """
    Simple check: verifies if generated text shares vocabulary with source docs.
    Very crude proxy for hallucination (0.0 = likely hallucination).
    """

    def check_consistency(self, generated_text: str, source_documents: list) -> float:
        if not source_documents:
            return 0.0 # No source, can't verify
        
        gen_words = set(generated_text.lower().split())
        source_words = set(" ".join(source_documents).lower().split())
        
        common = gen_words.intersection(source_words)
        if not gen_words:
            return 1.0
            
        return len(common) / len(gen_words)
