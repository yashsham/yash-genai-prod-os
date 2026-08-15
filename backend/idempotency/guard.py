import hashlib
from typing import Optional, Dict, Any

class IdempotencyGuard:
    """
    Idempotency & Duplicate Request Safeguard.
    Prevents duplicate API billing when users double-click buttons or network retries re-trigger requests.
    Computes a request fingerprint SHA-256(user_id + task + prompt + model) to return in-flight or cached results.
    """

    def __init__(self):
        self._in_flight: Dict[str, Dict[str, Any]] = {}
        self._completed: Dict[str, Dict[str, Any]] = {}

    def compute_fingerprint(self, user_id: str, prompt: str, task: str = "", model: str = "", idempotency_key: str = None) -> str:
        if idempotency_key:
            return f"key:{idempotency_key}"
        raw = f"{user_id}||{task}||{prompt}||{model}"
        return f"fp:{hashlib.sha256(raw.encode('utf-8')).hexdigest()}"

    def check_duplicate(self, fingerprint: str) -> Optional[Dict[str, Any]]:
        """
        Returns cached response if request with same fingerprint completed recently.
        """
        return self._completed.get(fingerprint)

    def mark_in_flight(self, fingerprint: str):
        self._in_flight[fingerprint] = {"status": "in_flight"}

    def mark_completed(self, fingerprint: str, response_data: Dict[str, Any]):
        if fingerprint in self._in_flight:
            del self._in_flight[fingerprint]
        self._completed[fingerprint] = response_data
