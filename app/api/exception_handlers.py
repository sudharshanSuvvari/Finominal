from fastapi.responses import JSONResponse

from app.core.exceptions import (
    NotFoundError, ConflictError, ForbiddenOperationError
)

def register_exception_handlers(app):

    @app.exception_handler(NotFoundError)
    async def not_found_handler(request, exc: NotFoundError):
        return JSONResponse(
            status_code=404,
            content={"detail": exc.message, "code": exc.code},
        )

    @app.exception_handler(ConflictError)
    async def conflict_handler(request, exc: ConflictError):
        return JSONResponse(
            status_code=409,
            content={"detail": exc.message, "code": exc.code},
        )

    @app.exception_handler(ForbiddenOperationError)
    async def forbidden_handler(request, exc: ForbiddenOperationError):
        return JSONResponse(
            status_code=403,
            content={"detail": exc.message, "code": exc.code},
        )