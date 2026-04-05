from pydantic import BaseModel
from decimal import Decimal
from datetime import date
from typing import Optional

class SummaryResponse(BaseModel):
    total_income: Decimal
    total_expenses: Decimal
    net_balance: Decimal
    total_records: int

class CategoryTotal(BaseModel):
    category: str
    type: str
    total: Decimal
    count: int

class CategoryBreakdownResponse(BaseModel):
    income: list[CategoryTotal]
    expenses: list[CategoryTotal]

class MonthlyTrend(BaseModel):
    year: int
    month: int
    month_label: str 
    total_income: Decimal
    total_expenses: Decimal
    net: Decimal

class TrendsResponse(BaseModel):
    trends: list[MonthlyTrend]

class RecentRecord(BaseModel):
    id: int
    amount: Decimal
    type: str
    category: str
    date: date
    notes: Optional[str]

class RecentActivityResponse(BaseModel):
    records: list[RecentRecord]
