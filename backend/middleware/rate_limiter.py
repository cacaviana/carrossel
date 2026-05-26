"""Rate limiting centralizado para endpoints de geracao (APIs pagas)."""
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.requests import Request
from starlette.responses import JSONResponse

limiter = Limiter(key_func=get_remote_address)

# Limites por categoria de endpoint
GENERATION_LIMIT = "5/minute"   # endpoints que chamam Claude/Gemini ($$$)
PIPELINE_LIMIT = "3/minute"     # pipeline executar (cadeia de chamadas)
CONFIG_WRITE_LIMIT = "10/minute"  # escrita de config/brands
DEFAULT_LIMIT = "60/minute"     # leitura geral


async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={
            "detail": f"Rate limit excedido. Tente novamente em alguns segundos.",
            "limit": str(exc.detail),
        },
    )
