from fastapi import Depends, Header
from sqlalchemy.orm import Session as DBSession
from datetime import datetime, timezone
from typing import Optional
from app.database import get_db
from app.models.user import User
from app.models.session import Session
from app.core.exceptions import UnauthorizedError

def get_current_user(
    authorization: Optional[str] = Header(default=None),
    db: DBSession = Depends(get_db)
) -> User:
    if not authorization:
        raise UnauthorizedError("No Authorization header provided. Please login.")
    if authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
    else:
        token = authorization.strip()

    session = db.query(Session).filter(Session.session_token == token).first()
    if not session:
        raise UnauthorizedError("Session not found. Please login again.")

    now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
    if session.expires_at < now_utc:
        db.delete(session)
        db.commit()
        raise UnauthorizedError("Session has expired. Please login again.")

    user = db.query(User).filter(User.id == session.user_id).first()
    if not user:
        raise UnauthorizedError("User associated with session no longer exists.")

    if user.status != "active":
        raise UnauthorizedError("Your account has been deactivated. Contact an administrator.")

    return user