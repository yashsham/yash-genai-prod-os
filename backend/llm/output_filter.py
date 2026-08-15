# Delegation to Security Framework
from backend.output_defense.redaction import PatternRedactor
from backend.output_defense.hallucination_check import NgramOverlapChecker

redactor = PatternRedactor()
hallucination_checker = NgramOverlapChecker()

def process_output(text: str, source_docs: list = None) -> str:
    """
    Sanitizes LLM output and optionally checks for consistency.
    """
    # 1. Hallucination Check (Warning only)
    if source_docs:
        score = hallucination_checker.check_consistency(text, source_docs)
        if score < 0.3:
            print(f"Warning: Low consistency score ({score:.2f}) - possible hallucination.")

    # 2. Redaction (Hard Enforcement)
    clean_text = redactor.redact(text)
    
    return clean_text
