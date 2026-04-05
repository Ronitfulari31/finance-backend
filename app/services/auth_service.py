import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session as DBSession
from app.models.user import User
from app.models.session import Session
from app.core.config import SESSION_MAX_AGE_SECONDS
from app.core.exceptions import UnauthorizedError


def hash_password(plain: str) -> str:
    return hashlib.sha256(plain.encode()).hexdigest()

def verify_password(plain: str, hashed: str) -> bool:
    return hash_password(plain) == hashed

def login(email: str, password: str, db: DBSession) -> dict:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise UnauthorizedError("Invalid email or password.")
    if user.status != "active":
        raise UnauthorizedError("Your account is deactivated. Please contact an administrator.")

    token = secrets.token_hex(48)

    expires_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(
        seconds=SESSION_MAX_AGE_SECONDS
    )
    session = Session(
        user_id=user.id,
        session_token=token,
        expires_at=expires_at
    )
    db.add(session)
    db.commit()

    return {
        "message": "Login successful.",
        "session_token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }

def logout(token: str, db: DBSession) -> dict:
    session = db.query(Session).filter(Session.session_token == token).first()
    if session:
        db.delete(session)
        db.commit()
    return {"message": "Logged out successfully."}
