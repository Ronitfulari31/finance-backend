from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DBSession
from app.database import get_db
from app.schemas.dashboard import (
    SummaryResponse,
    CategoryBreakdownResponse,
    TrendsResponse,
    RecentActivityResponse
)
from app.services import dashboard_service
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary", response_model=SummaryResponse, summary="Total income, expenses and net balance")
def summary(
    current_user=Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    return dashboard_service.get_summary(db)

@router.get("/by-category", response_model=CategoryBreakdownResponse, summary="Totals grouped by category")
def by_category(
    current_user=Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    return dashboard_service.get_by_category(db)

@router.get("/trends", response_model=TrendsResponse, summary="Month-by-month income vs expenses (last 12 months)")
def trends(
    current_user=Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    return dashboard_service.get_monthly_trends(db)

@router.get("/recent", response_model=RecentActivityResponse, summary="Most recent 10 transactions")
def recent(
    current_user=Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    return dashboard_service.get_recent_activity(db)
