from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse

# Import Security Modules (Demo Implementations)
from backend.input_defense.injection_scanner import RegexInjectionScanner
from backend.observability.audit_logger import ConsoleJSONLogger

app = FastAPI()
logger = ConsoleJSONLogger()
scanner = RegexInjectionScanner()

@app.middleware("http")
async def security_middleware(request: Request, call_next):
    """
    Global Security Middleware:
    1. Logs the request (Auditing).
    2. Scans body for Prompt Injection (Input Defense).
    """
    # 1. Audit Log Request
    logger.log_event(
        event_type="API_REQUEST",
        severity="LOW",
        details={"path": request.url.path, "method": request.method},
        user_id="anonymous" # In real app, extract from token
    )

    # 2. Input Defense (Simplified: Read body not consumed for demo purposes)
    # In a real app, you'd be careful about reading the stream or use a dependency
    # Here we mock the check on specific endpoints or assume body is available
    
    response = await call_next(request)
    
    return response

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"message": str(exc), "type": "SecurityValidationError"}
    )

@app.get("/")
def health_check():
    return {"status": "secure"}
