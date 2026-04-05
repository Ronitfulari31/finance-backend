import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from datetime import date, timedelta
import random
from app.database import SessionLocal, engine, Base
from app.models import User, FinancialRecord
from app.services.auth_service import hash_password
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

db = SessionLocal()

users = [
    User(
        name="Alice Admin",
        email="admin@finance.com",
        password_hash=hash_password("admin123"),
        role="admin",
        status="active"
    ),
    User(
        name="Bob Analyst",
        email="analyst@finance.com",
        password_hash=hash_password("analyst123"),
        role="analyst",
        status="active"
    ),
    User(
        name="Victor Viewer",
        email="viewer@finance.com",
        password_hash=hash_password("viewer123"),
        role="viewer",
        status="active"
    ),
]

db.add_all(users)
db.commit()
for u in users:
    db.refresh(u)

admin = users[0]

income_categories = ["Salary", "Freelance", "Investments", "Rental Income", "Bonus"]
expense_categories = ["Rent", "Food", "Transport", "Utilities", "Healthcare", "Entertainment", "Insurance"]

records = []
today = date.today()

for i in range(30):
    record_date = today - timedelta(days=random.randint(0, 365))
    is_income = random.random() > 0.45  

    if is_income:
        category = random.choice(income_categories)
        amount = round(random.uniform(500, 8000), 2)
    else:
        category = random.choice(expense_categories)
        amount = round(random.uniform(50, 2000), 2)

    records.append(FinancialRecord(
        created_by=admin.id,
        amount=amount,
        type="income" if is_income else "expense",
        category=category,
        date=record_date,
        notes=f"Sample {category.lower()} record #{i+1}",
        deleted_at=None
    ))

db.add_all(records)
db.commit()
db.close()

print(" Database seeded successfully!")
print()
print("Login credentials:")
print("  admin@finance.com    / admin123")
print("  analyst@finance.com  / analyst123")
print("  viewer@finance.com   / viewer123")
print()
print("Start the server with: uvicorn app.main:app --reload")
print("API docs available at: http://localhost:8000/docs")
