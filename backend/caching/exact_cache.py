import hashlib
import json
from typing import Optional, Dict, Any

class ExactResponseCache:
    """
    Fast exact-match KV response cache.
    Hashes system prompt + user input + params into a unique SHA-256 key.
    Delivers zero API cost responses for identical repeated queries (FAQs, static classification).
    """

    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}

    def _compute_key(self, prompt: str, system_prompt: str = "", model: str = "") -> str:
        raw_str = f"{system_prompt}||{prompt}||{model}"
        return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()

    def get(self, prompt: str, system_prompt: str = "", model: str = "") -> Optional[Dict[str, Any]]:
        key = self._compute_key(prompt, system_prompt, model)
        return self._cache.get(key)

    def set(self, prompt: str, response_data: Dict[str, Any], system_prompt: str = "", model: str = ""):
        key = self._compute_key(prompt, system_prompt, model)
        self._cache[key] = response_data
