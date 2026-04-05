from sqlalchemy.orm import Session as DBSession
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.services.auth_service import hash_password
from app.core.exceptions import NotFoundError, ConflictError

def get_all_users(db: DBSession, page: int = 1, limit: int = 20) -> dict:
    offset = (page - 1) * limit
    total = db.query(User).count()
    users = db.query(User).offset(offset).limit(limit).all()
    return {"total": total, "page": page, "limit": limit, "users": users}

def get_user_by_id(user_id: int, db: DBSession) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundError("User")
    return user

def create_user(data: UserCreate, db: DBSession) -> User:
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise ConflictError(f"An account with email '{data.email}' already exists.")
    user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
        role=data.role,
        status="active"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_user(user_id: int, data: UserUpdate, db: DBSession) -> User:
    user = get_user_by_id(user_id, db)

    if data.name is not None:
        user.name = data.name
    if data.role is not None:
        user.role = data.role
    if data.status is not None:
        user.status = data.status

    db.commit()
    db.refresh(user)
    return user

def delete_user(user_id: int, current_user, db: DBSession) -> dict:
    if current_user.id == user_id:
        raise ConflictError("You cannot delete your own account.")
    user = get_user_by_id(user_id, db)
    db.delete(user)
    db.commit()
    return {"message": f"User '{user.name}' (id={user_id}) has been deleted."}
