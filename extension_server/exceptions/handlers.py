from fastapi import Request
from fastapi.responses import JSONResponse

from exceptions.errors import ExtensionValidationError


async def base_exception_handler(request: Request, exc: ExtensionValidationError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "invalid", "reason": exc.reason},
    )


def register_exception_handlers(app):
    app.add_exception_handler(ExtensionValidationError, base_exception_handler)
