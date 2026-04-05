from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, ForeignKey, Text, func
from app.database import Base

class FinancialRecord(Base):
    __tablename__ = "financial_records"
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    amount = Column(Numeric(12, 2), nullable=False)
    type = Column(String(10), nullable=False)       
    category = Column(String(100), nullable=False)  
    date = Column(Date, nullable=False)
    notes = Column(Text, nullable=True)
    deleted_at = Column(DateTime, nullable=True, default=None)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def __repr__(self):
        return f"<FinancialRecord id={self.id} type={self.type} amount={self.amount}>"
