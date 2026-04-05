from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session as DBSession
from datetime import date
from typing import Optional
from app.database import get_db
from app.schemas.record import RecordCreate, RecordUpdate, RecordResponse, RecordListResponse
from app.services import record_service
from app.dependencies.rbac import require_role

router = APIRouter(prefix="/records", tags=["Financial Records"])

@router.get("", response_model=RecordListResponse, summary="List records with filters (Analyst, Admin)")
def list_records(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    type_filter: Optional[str] = Query(None, alias="type", description="Filter by type: income or expense"),
    category: Optional[str] = Query(None, description="Filter by category (partial match)"),
    date_from: Optional[date] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="End date filter (YYYY-MM-DD)"),
    current_user=Depends(require_role("analyst", "admin")),
    db: DBSession = Depends(get_db)
):
    return record_service.get_all_records(db, page, limit, type_filter, category, date_from, date_to)

@router.post("", response_model=RecordResponse, status_code=201, summary="Create a record (Admin only)")
def create_record(
    payload: RecordCreate,
    current_user=Depends(require_role("admin")),
    db: DBSession = Depends(get_db)
):
    return record_service.create_record(payload, current_user.id, db)

@router.get("/{record_id}", response_model=RecordResponse, summary="Get a single record (Analyst, Admin)")
def get_record(
    record_id: int,
    current_user=Depends(require_role("analyst", "admin")),
    db: DBSession = Depends(get_db)
):
    return record_service.get_record_by_id(record_id, db)

@router.patch("/{record_id}", response_model=RecordResponse, summary="Update a record (Admin only)")
def update_record(
    record_id: int,
    payload: RecordUpdate,
    current_user=Depends(require_role("admin")),
    db: DBSession = Depends(get_db)
):
    return record_service.update_record(record_id, payload, db)

@router.delete("/{record_id}", summary="Soft delete a record (Admin only)")
def delete_record(
    record_id: int,
    current_user=Depends(require_role("admin")),
    db: DBSession = Depends(get_db)
):
    return record_service.soft_delete_record(record_id, db)