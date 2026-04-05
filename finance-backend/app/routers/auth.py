from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session as DBSession
from typing import Optional
from app.database import get_db
from app.schemas.auth import LoginRequest, LoginResponse
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=LoginResponse, summary="Login and start a session")
def login(payload: LoginRequest, db: DBSession = Depends(get_db)):
    return auth_service.login(payload.email, payload.password, db)

@router.post("/logout", summary="End the current session")
def logout(
    authorization: Optional[str] = Header(default=None),
    db: DBSession = Depends(get_db)
):
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]

    if not token:
        return {"message": "No active session to logout from."}

    return auth_service.logout(token, db)
