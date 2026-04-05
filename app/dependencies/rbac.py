from fastapi import Depends
from app.models.user import User
from app.dependencies.auth import get_current_user
from app.core.exceptions import ForbiddenError

def require_role(*allowed_roles: str):
    def check_role(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise ForbiddenError(
                f"Access denied. This action requires one of these roles: {', '.join(allowed_roles)}. "
                f"Your current role is: {current_user.role}."
            )
        return current_user

    return check_role
