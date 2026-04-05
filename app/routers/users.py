from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session as DBSession
from app.database import get_db
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserListResponse
from app.services import user_service
from app.dependencies.rbac import require_role

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("", response_model=UserListResponse, summary="List all users (Admin only)")
def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Results per page"),
    current_user=Depends(require_role("admin")),
    db: DBSession = Depends(get_db)
):
    return user_service.get_all_users(db, page, limit)

@router.post("", response_model=UserResponse, status_code=201, summary="Create a new user (Admin only)")
def create_user(
    payload: UserCreate,
    current_user=Depends(require_role("admin")),
    db: DBSession = Depends(get_db)
):
    return user_service.create_user(payload, db)

@router.get("/{user_id}", response_model=UserResponse, summary="Get a user by ID (Admin only)")
def get_user(
    user_id: int,
    current_user=Depends(require_role("admin")),
    db: DBSession = Depends(get_db)
):
    return user_service.get_user_by_id(user_id, db)

@router.patch("/{user_id}", response_model=UserResponse, summary="Update a user's role or status (Admin only)")
def update_user(
    user_id: int,
    payload: UserUpdate,
    current_user=Depends(require_role("admin")),
    db: DBSession = Depends(get_db)
):
    return user_service.update_user(user_id, payload, db)

@router.delete("/{user_id}", summary="Delete a user (Admin only)")
def delete_user(
    user_id: int,
    current_user=Depends(require_role("admin")),
    db: DBSession = Depends(get_db)
):
    return user_service.delete_user(user_id, current_user, db)
