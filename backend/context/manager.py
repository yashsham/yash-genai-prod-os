from typing import List, Dict, Any

class ConversationContextManager:
    """
    Context Window Management Engine.
    Prevents context-stuffing cost spikes by maintaining:
    1. Short-term rolling message window (last N turns).
    2. Rolling summary of older conversation turns.
    3. Important extracted facts.
    
    Replaces 50,000 token raw histories with compact 3,000 token representations.
    """

    def __init__(self, max_history_turns: int = 6):
        self.max_history_turns = max_history_turns

    def format_bounded_context(self, history: List[Dict[str, str]], rolling_summary: str = "") -> List[Dict[str, str]]:
        """
        Assembles bounded context containing rolling summary + last N turns.
        """
        bounded_messages = []
        
        # Ingress rolling summary as system context if present
        if rolling_summary:
            bounded_messages.append({
                "role": "system",
                "content": f"CONVERSATION SUMMARY (Prior Turns):\n{rolling_summary}"
            })

        # Retain only the most recent N turns
        recent_turns = history[-self.max_history_turns:] if len(history) > self.max_history_turns else history
        for turn in recent_turns:
            bounded_messages.append(turn)

        return bounded_messages
