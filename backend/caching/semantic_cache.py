import math
from typing import Optional, Dict, Any, List

class SemanticCache:
    """
    Semantic Vector Cache using Cosine Similarity matching.
    Reuses answers for semantically identical queries (e.g. "What's the refund policy?" vs "How to get refund?").
    Enforces a strict confidence similarity threshold tau >= 0.94 to avoid semantic drift.
    """

    def __init__(self, similarity_threshold: float = 0.94):
        self.similarity_threshold = similarity_threshold
        # Cache entries: list of {"query": str, "vector": list[float], "response": dict}
        self._entries: List[Dict[str, Any]] = []

    def _mock_embed(self, text: str) -> List[float]:
        """
        Mock lightweight embedding generator. In production, uses fast embedding model or Redis Vector Search.
        """
        # Create deterministic pseudo-vector based on character frequencies
        words = text.lower().split()
        vec = [0.0] * 10
        for w in words:
            vec[hash(w) % 10] += 1.0
        norm = math.sqrt(sum(x*x for x in vec)) or 1.0
        return [x / norm for x in vec]

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        dot = sum(a * b for a, b in zip(vec1, vec2))
        return dot

    def lookup(self, query: str) -> Optional[Dict[str, Any]]:
        query_vec = self._mock_embed(query)
        best_score = 0.0
        best_response = None

        for entry in self._entries:
            sim = self._cosine_similarity(query_vec, entry["vector"])
            if sim > best_score:
                best_score = sim
                best_response = entry["response"]

        if best_score >= self.similarity_threshold and best_response:
            return {
                "response": best_response,
                "similarity_score": round(best_score, 4),
                "semantic_hit": True
            }
        return None

    def store(self, query: str, response_data: Dict[str, Any]):
        query_vec = self._mock_embed(query)
        self._entries.append({
            "query": query,
            "vector": query_vec,
            "response": response_data
        })
