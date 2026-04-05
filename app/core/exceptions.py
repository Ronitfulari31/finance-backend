from fastapi import HTTPException, status

class AppError(HTTPException):
    def __init__(self, status_code: int, message: str):
        super().__init__(status_code=status_code, detail=message)

class NotFoundError(AppError):
    def __init__(self, resource: str = "Resource"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=f"{resource} not found."
        )

class UnauthorizedError(AppError):
    def __init__(self, message: str = "Authentication required. Please login."):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=message
        )

class ForbiddenError(AppError):
    def __init__(self, message: str = "You do not have permission to perform this action."):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            message=message
        )

class ConflictError(AppError):
    def __init__(self, message: str = "A conflict occurred with existing data."):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            message=message
        )

class ValidationError(AppError):
    def __init__(self, message: str = "Invalid input data."):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message=message
        )
