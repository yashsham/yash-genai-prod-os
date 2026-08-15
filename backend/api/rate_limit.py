from fastapi import Request, HTTPException
from backend.api_security.rate_limiting import InMemoryRateLimiter

# Global limiter instance
limiter = InMemoryRateLimiter(max_requests=10)

async def check_rate_limit(request: Request):
    """
    Dependency to check rate limit for the client IP.
    """
    client_ip = request.client.host if request.client else "unknown"
    
    if not limiter.check_limit(client_ip, request.url.path):
        raise HTTPException(
            status_code=429,
            detail="Too Many Requests"
        )
    return True
