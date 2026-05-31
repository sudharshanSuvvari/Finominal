# app/core/exceptions.py

class AppException(Exception):
    def __init__(self, message: str, code: str = "APP_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)

class NotFoundError(AppException):
    def __init__(self, message="Resource not found"):
        super().__init__(message, code="NOT_FOUND")


class ConflictError(AppException):
    def __init__(self, message="Conflict occurred"):
        super().__init__(message, code="CONFLICT")


class ForbiddenOperationError(AppException):
    def __init__(self, message="Operation not allowed"):
        super().__init__(message, code="FORBIDDEN")

class TokenExpiredError(Exception):
    """Token is structurally valid but the exp claim has passed."""

class TokenInvalidError(Exception):
    """Token is malformed, signed with the wrong key, or has an unexpected type."""