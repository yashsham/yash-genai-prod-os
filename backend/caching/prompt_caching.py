from typing import List, Dict, Any

class PromptPrefixArchitect:
    """
    Architects prompt structures to exploit provider-side prompt caching (Anthropic / OpenAI prefix caching).
    Ensures static content (System Instructions, Tool Schemas, Reference Specs) comes FIRST,
    and dynamic content (User input, turn history) comes LAST to maximize cache hits (50%-90% discount).
    """

    @staticmethod
    def construct_cached_payload(
        system_persona: str,
        tool_schemas: List[Dict[str, Any]],
        knowledge_docs: List[str],
        user_query: str,
        chat_history: List[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Assembles messages with deterministic ordering and Anthropic/OpenAI cache markers.
        """
        # 1. Static Prefix Block (System Persona + Tool Schemas + Static Knowledge Docs)
        static_prefix = (
            f"=== SYSTEM PERSONA ===\n{system_persona}\n\n"
            f"=== ALLOWED TOOLS ===\n{tool_schemas}\n\n"
            f"=== KNOWLEDGE CONTEXT ===\n" + "\n---\n".join(knowledge_docs)
        )

        messages = [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": static_prefix,
                        "cache_control": {"type": "ephemeral"} # Anthropic prompt caching flag
                    }
                ]
            }
        ]

        # 2. Dynamic Turn Block (Chat History + User Query)
        if chat_history:
            for msg in chat_history:
                messages.append(msg)

        messages.append({
            "role": "user",
            "content": user_query
        })

        return messages
