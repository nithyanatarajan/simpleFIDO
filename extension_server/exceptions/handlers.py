from fastapi import Request
from fastapi.responses import JSONResponse

from exceptions import TokenValidationError


async def token_validation_exception_handler(request: Request, exc: TokenValidationError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "invalid", "reason": exc.reason},
    )


def register_exception_handlers(app):
    app.add_exception_handler(TokenValidationError, token_validation_exception_handler)
