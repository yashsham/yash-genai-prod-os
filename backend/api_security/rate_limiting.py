from abc import ABC, abstractmethod
import time
from collections import defaultdict
from typing import Dict, Tuple

class MultiDimensionalRateLimiter:
    """
    Token-Aware, Cost-Aware Multi-Dimensional Rate Limiter.
    Enforces RPM (Requests/min), TPM (Tokens/min), ITPM (Input tokens/min),
    OTPM (Output tokens/min), and Concurrency limits.
    Prevents Denial-of-Wallet (DoW) attacks via oversized payloads.
    """

    def __init__(
        self,
        max_rpm: int = 30,
        max_tpm: int = 100_000,
        max_itpm: int = 80_000,
        max_otpm: int = 20_000,
        max_concurrency: int = 3
    ):
        self.max_rpm = max_rpm
        self.max_tpm = max_tpm
        self.max_itpm = max_itpm
        self.max_otpm = max_otpm
        self.max_concurrency = max_concurrency

        # Stores timestamps of requests and token counts: (timestamp, tokens, is_input)
        self.user_requests = defaultdict(list)
        self.active_concurrency = defaultdict(int)

    def acquire_concurrency(self, user_id: str) -> bool:
        """
        Attempts to acquire a concurrency slot for active processing.
        """
        if self.active_concurrency[user_id] >= self.max_concurrency:
            return False
        self.active_concurrency[user_id] += 1
        return True

    def release_concurrency(self, user_id: str):
        """
        Releases an active concurrency slot upon request completion.
        """
        if self.active_concurrency[user_id] > 0:
            self.active_concurrency[user_id] -= 1

    def check_limits(self, user_id: str, estimated_input_tokens: int = 1000, max_output_tokens: int = 1024) -> Tuple[bool, str]:
        """
        Checks multi-dimensional sliding window rate limits over a 60-second window.
        """
        now = time.time()
        window_start = now - 60.0

        # Prune events older than 60 seconds
        self.user_requests[user_id] = [
            ev for ev in self.user_requests[user_id] if ev[0] > window_start
        ]

        history = self.user_requests[user_id]
        
        # 1. RPM Check
        current_rpm = len(history)
        if current_rpm >= self.max_rpm:
            return False, f"RPM limit exceeded ({current_rpm}/{self.max_rpm} req/min)"

        # 2. ITPM & TPM Check
        current_itpm = sum(ev[1] for ev in history if ev[2]) # input tokens
        current_otpm = sum(ev[1] for ev in history if not ev[2]) # output tokens
        current_tpm = current_itpm + current_otpm

        if current_itpm + estimated_input_tokens > self.max_itpm:
            return False, f"Input Token limit (ITPM) exceeded ({current_itpm + estimated_input_tokens}/{self.max_itpm} tokens/min)"

        if current_tpm + estimated_input_tokens + max_output_tokens > self.max_tpm:
            return False, f"Total Token limit (TPM) exceeded ({current_tpm + estimated_input_tokens + max_output_tokens}/{self.max_tpm} tokens/min)"

        # Record this request attempt
        self.user_requests[user_id].append((now, estimated_input_tokens, True))
        return True, "Rate limit check passed"
