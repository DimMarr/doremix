import os
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from fastapi.responses import JSONResponse

# On récupère la limite de taux de requêtes depuis les variables d'environnement
RATE_LIMIT = os.getenv("RATE_LIMIT", "100/minute")

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[RATE_LIMIT],
    storage_uri=os.getenv("RATE_LIMIT_STORAGE", "memory://"),
    headers_enabled=True,
)


# Gestionnaire d'erreur pour le dépassement de la limite de taux de requêtes
async def rate_limit_exceeded_handler(
    request: Request, exc: RateLimitExceeded
) -> Response:
    """
    Custom handler for rate limit exceeded errors
    """
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "message": "Too many requests. Please try again later.",
            "detail": str(exc.detail),
        },
        headers=exc.headers,
    )
