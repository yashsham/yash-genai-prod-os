from abc import ABC, abstractmethod

class AuthenticationFlow(ABC):
    """
    Abstract base class for authentication mechanisms.
    """

    @abstractmethod
    def authenticate_request(self, token: str) -> dict:
        """
        Validates the token and returns the user context.
        """
        pass

    @abstractmethod
    def issue_token(self, user_id: str, scopes: list) -> str:
        """
        Issues a new access token.
        """
        pass

import json
import base64

class SimpleAuthFlow(AuthenticationFlow):
    """
    Mock JWT implementation. 
    """

    def authenticate_request(self, token: str) -> dict:
        if not token.startswith("Bearer "):
            raise ValueError("Invalid token format")
        
        token_val = token.split(" ")[1]
        try:
            # Mock decoding (in reality use jwt.decode)
            decoded = json.loads(base64.b64decode(token_val).decode())
            return decoded
        except Exception:
            raise ValueError("Invalid token")

    def issue_token(self, user_id: str, scopes: list) -> str:
        payload = {"sub": user_id, "scopes": scopes}
        # Mock signing (in reality use jwt.encode)
        token_str = base64.b64encode(json.dumps(payload).encode()).decode()
        return f"Bearer {token_str}"
