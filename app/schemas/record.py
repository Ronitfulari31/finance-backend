from pydantic import BaseModel, field_validator
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Literal

TWO_PLACES = Decimal("0.01")

class RecordCreate(BaseModel):
    amount: Decimal
    type: Literal["income", "expense"]
    category: str
    date: date
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Amount must be greater than zero.")
        return v.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

    @field_validator("category")
    @classmethod
    def category_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Category cannot be empty.")
        return v.strip()

class RecordUpdate(BaseModel):
    amount: Optional[Decimal] = None
    type: Optional[Literal["income", "expense"]] = None
    category: Optional[str] = None
    date: Optional[date] = None
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v <= 0:
            raise ValueError("Amount must be greater than zero.")
        return v.quantize(TWO_PLACES, rounding=ROUND_HALF_UP) if v is not None else v

    @field_validator("category")
    @classmethod
    def category_must_not_be_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("Category cannot be empty.")
        return v.strip() if v else v

class RecordResponse(BaseModel):
    id: int
    created_by: Optional[int]
    amount: Decimal
    type: str
    category: str
    date: date
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class RecordListResponse(BaseModel):
    total: int
    page: int
    limit: int
    records: list[RecordResponse]