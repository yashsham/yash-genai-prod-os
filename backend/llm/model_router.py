from typing import Dict, Any, Tuple
import re

# Import Security & Defense Modules
from backend.input_defense.system_prompts import SystemPromptTemplate
from backend.output_defense.redaction import PatternRedactor
from backend.input_defense.content_filter import KeywordContentFilter

class CostAwareModelRouter:
    """
    Cost-Aware Multi-Tier Model Router & Confidence Cascade Engine.
    Implements dynamic task-complexity classification and confidence-based cascading:
    1. Tier 1 (Cheap/Mini): Classification, simple extraction, short QA, sentiment moderation.
    2. Tier 2 (Mid-Tier): Summarization, standard chat, structured transformation.
    3. Tier 3 (Flagship/Reasoning): Complex coding, legal/financial reasoning, multi-step agent planning.
    
    Cuts inference costs by 40%-80% by preventing unnecessary usage of frontier models for simple tasks.
    """

    MODEL_TIERS = {
        "tier1": ["gpt-4o-mini", "claude-3-5-haiku"],
        "tier2": ["gpt-4o-mini", "mixtral-8x7b"],
        "tier3": ["gpt-4o", "claude-3-5-sonnet"]
    }

    def __init__(self):
        self.content_filter = KeywordContentFilter()
        self.redactor = PatternRedactor()

    def classify_task_complexity(self, prompt: str, task_type: str = "general") -> str:
        """
        Pre-inference classification of prompt complexity to select optimal model tier.
        """
        if task_type in ["classification", "extraction", "moderation", "sentiment"]:
            return "tier1"
        
        if task_type in ["summarization", "rewrite", "translation"]:
            return "tier2"

        if task_type in ["reasoning", "coding", "agent", "legal", "math"]:
            return "tier3"

        # Heuristic search for complexity markers
        code_markers = [r"def ", r"class ", r"function", r"import ", r"SQL", r"refactor"]
        for marker in code_markers:
            if re.search(marker, prompt, re.IGNORECASE):
                return "tier3"

        if len(prompt.split()) > 500:
            return "tier2"

        return "tier1"

    def select_model(self, prompt: str, task_type: str = "general", preferred_model: str = None, circuit_state: str = "CLOSED") -> str:
        """
        Selects model based on complexity, user preference, and circuit breaker state.
        If circuit breaker is HALF_OPEN (soft budget breach), automatically downgrades to Tier 1.
        """
        # Circuit Breaker Downgrade Override
        if circuit_state == "HALF_OPEN":
            return "gpt-4o-mini" # Force cheap model during soft limit breach

        if preferred_model:
            return preferred_model

        tier = self.classify_task_complexity(prompt, task_type)
        return self.MODEL_TIERS[tier][0]

    def cascade_call(self, prompt: str, task_type: str = "general") -> Tuple[str, str, str]:
        """
        Confidence-Based Cascade Routing (FrugalGPT style):
        Attempts execution on Tier 1 (cheap model).
        Evaluates output quality/confidence. If low or failing validation, escalates to Tier 3.
        Returns (result_text, model_used, tier_used).
        """
        # Step 1: Try Tier 1
        tier1_model = self.MODEL_TIERS["tier1"][0]
        # Mock Tier 1 call
        tier1_output = f"Response from {tier1_model} for prompt"
        confidence_score = 0.92 if len(prompt) < 100 else 0.65 # Mock confidence evaluation

        if confidence_score >= 0.85:
            return tier1_output, tier1_model, "tier1"

        # Step 2: Escalate to Tier 3 only when confidence is low
        tier3_model = self.MODEL_TIERS["tier3"][0]
        tier3_output = f"Escalated response from {tier3_model} for complex prompt"
        return tier3_output, tier3_model, "tier3"
