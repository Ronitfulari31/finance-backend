from decimal import Decimal
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import text

def get_summary(db: DBSession) -> dict:
    
    result = db.execute(text("""
        SELECT
            COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) AS total_income,
            COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) AS total_expenses,
            COUNT(*) AS total_records
        FROM financial_records
        WHERE deleted_at IS NULL
    """)).fetchone()

    total_income = Decimal(str(result.total_income))
    total_expenses = Decimal(str(result.total_expenses))

    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_balance": total_income - total_expenses,
        "total_records": result.total_records
    }


def get_by_category(db: DBSession) -> dict:
    rows = db.execute(text("""
        SELECT
            category,
            type,
            SUM(amount) AS total,
            COUNT(*) AS count
        FROM financial_records
        WHERE deleted_at IS NULL
        GROUP BY category, type
        ORDER BY type, total DESC
    """)).fetchall()

    income = []
    expenses = []

    for row in rows:
        entry = {
            "category": row.category,
            "type": row.type,
            "total": Decimal(str(row.total)),
            "count": row.count
        }
        if row.type == "income":
            income.append(entry)
        else:
            expenses.append(entry)

    return {"income": income, "expenses": expenses}


def get_monthly_trends(db: DBSession) -> dict:
    rows = db.execute(text("""
        SELECT
            strftime('%Y', date) AS year,
            strftime('%m', date) AS month,
            SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) AS total_income,
            SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) AS total_expenses
        FROM financial_records
        WHERE deleted_at IS NULL
          AND date >= date('now', '-12 months')
        GROUP BY year, month
        ORDER BY year ASC, month ASC
    """)).fetchall()

    month_names = {
        "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr",
        "05": "May", "06": "Jun", "07": "Jul", "08": "Aug",
        "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec"
    }

    trends = []
    for row in rows:
        income = Decimal(str(row.total_income))
        expenses = Decimal(str(row.total_expenses))
        trends.append({
            "year": int(row.year),
            "month": int(row.month),
            "month_label": f"{month_names[row.month]} {row.year}",
            "total_income": income,
            "total_expenses": expenses,
            "net": income - expenses
        })

    return {"trends": trends}


def get_recent_activity(db: DBSession, limit: int = 10) -> dict:
    rows = db.execute(text("""
        SELECT id, amount, type, category, date, notes
        FROM financial_records
        WHERE deleted_at IS NULL
        ORDER BY date DESC, created_at DESC
        LIMIT :limit
    """), {"limit": limit}).fetchall()

    records = [
        {
            "id": row.id,
            "amount": Decimal(str(row.amount)),
            "type": row.type,
            "category": row.category,
            "date": row.date,
            "notes": row.notes
        }
        for row in rows
    ]

    return {"records": records}
