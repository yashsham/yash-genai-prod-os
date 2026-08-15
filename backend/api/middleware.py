import json
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from backend.input_defense.injection_scanner import RegexInjectionScanner

class AISecurityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.scanner = RegexInjectionScanner()

    async def dispatch(self, request: Request, call_next):
        # Only scan POST requests to chat/completions
        if request.method == "POST" and "chat" in request.url.path:
            body_bytes = await request.body()
            try:
                body_json = json.loads(body_bytes)
                prompt = body_json.get("prompt", "")
                
                # Scan for injection
                scan_result = self.scanner.scan_prompt(prompt)
                if not scan_result["is_safe"]:
                    return JSONResponse(
                        status_code=403,
                        content={
                            "error": "Prompt Injection Detected",
                            "details": scan_result["reason"]
                        }
                    )
            except Exception:
                pass # Malformed JSON or other error, let app handle or block

        response = await call_next(request)
        return response
