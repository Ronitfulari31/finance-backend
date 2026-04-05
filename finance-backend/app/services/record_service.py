from datetime import datetime, timezone, date
from decimal import Decimal
from typing import Optional
from sqlalchemy.orm import Session as DBSession
from app.models.record import FinancialRecord
from app.schemas.record import RecordCreate, RecordUpdate
from app.core.exceptions import NotFoundError


def _base_query(db: DBSession):
    return db.query(FinancialRecord).filter(FinancialRecord.deleted_at == None)


def get_all_records(
    db: DBSession,
    page: int = 1,
    limit: int = 20,
    type_filter: Optional[str] = None,
    category: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
) -> dict:
    query = _base_query(db)

    if type_filter:
        query = query.filter(FinancialRecord.type == type_filter)
    if category:
        query = query.filter(FinancialRecord.category.ilike(f"%{category}%"))
    if date_from:
        query = query.filter(FinancialRecord.date >= date_from)
    if date_to:
        query = query.filter(FinancialRecord.date <= date_to)

    total = query.count()
    offset = (page - 1) * limit
    records = query.order_by(FinancialRecord.date.desc()).offset(offset).limit(limit).all()

    return {"total": total, "page": page, "limit": limit, "records": records}

def get_record_by_id(record_id: int, db: DBSession) -> FinancialRecord:
    record = _base_query(db).filter(FinancialRecord.id == record_id).first()
    if not record:
        raise NotFoundError("Financial record")
    return record

def create_record(data: RecordCreate, created_by_id: int, db: DBSession) -> FinancialRecord:
    record = FinancialRecord(
        created_by=created_by_id,
        amount=data.amount,
        type=data.type,
        category=data.category,
        date=data.date,
        notes=data.notes,
        deleted_at=None
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def update_record(record_id: int, data: RecordUpdate, db: DBSession) -> FinancialRecord:
    record = get_record_by_id(record_id, db)

    if data.amount is not None:
        record.amount = data.amount
    if data.type is not None:
        record.type = data.type
    if data.category is not None:
        record.category = data.category
    if data.date is not None:
        record.date = data.date
    if data.notes is not None:
        record.notes = data.notes

    db.commit()
    db.refresh(record)
    return record

def soft_delete_record(record_id: int, db: DBSession) -> dict:
    record = get_record_by_id(record_id, db)
    record.deleted_at = datetime.now(timezone.utc).replace(tzinfo=None)
    db.commit()
    return {"message": f"Record {record_id} has been deleted."}