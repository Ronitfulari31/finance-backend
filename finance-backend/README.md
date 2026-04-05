# Finance Data Processing and Access Control Backend

A RESTful backend API built with **Python + FastAPI + SQLite** for managing financial records with role-based access control (RBAC).

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Seed the database with sample data
python seed.py

# 3. Start the development server
uvicorn app.main:app --reload
```

API is now live at **http://localhost:8000**
Interactive docs (Swagger UI) at **http://localhost:8000/docs**


## Test Credentials (after seeding)

| Role     | Email                  | Password    |
|----------|------------------------|-------------|
| Admin    | admin@finance.com      | admin123    |
| Analyst  | analyst@finance.com    | analyst123  |
| Viewer   | viewer@finance.com     | viewer123   |

---

## Authentication

This API uses **session-based authentication**.

**Login:**
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@finance.com", "password": "admin123"}'
```

Response:
```json
{
  "message": "Login successful.",
  "session_token": "abc123...",
  "user": { "id": 1, "name": "Alice Admin", "email": "...", "role": "admin" }
}
```

**Use the token** in all subsequent requests:
```
Authorization: Bearer <session_token>
```

**Logout:**
```bash
curl -X POST http://localhost:8000/auth/logout \
  -H "Authorization: Bearer <session_token>"
```


## Role Permission Matrix

| Action                        | Viewer | Analyst | Admin  |
|-------------------------------|--------|---------|--------|
| View dashboard summary        | Yes    | Yes     | Yes    |
| View category breakdown       | Yes    | Yes     | Yes    |
| View monthly trends           | Yes    | Yes     | Yes    |
| View recent activity          | Yes    | Yes     | Yes    |
| List financial records        | No     | Yes     | Yes    |
| Filter / search records       | No     | Yes     | Yes    |
| Get single record             | No     | Yes     | Yes    |
| Create record                 | No     | No      | Yes    |
| Update record                 | No     | No      | Yes    |
| Delete record (soft)          | No     | No      | Yes    |
| List users                    | No     | No      | Yes    |
| Create user                   | No     | No      | Yes    |
| Get user by ID                | No     | No      | Yes    |
| Update user role/status       | No     | No      | Yes    |
| Delete user                   | No     | No      | Yes    |

## API Endpoints

### Authentication
| Method | Endpoint       | Description                    |
|--------|----------------|--------------------------------|
| POST   | /auth/login    | Login and receive session token|
| POST   | /auth/logout   | Invalidate current session     |

### Users (Admin only)
| Method | Endpoint        | Description                      |
|--------|-----------------|----------------------------------|
| GET    | /users          | List all users (paginated)       |
| POST   | /users          | Create a new user                |
| GET    | /users/{id}     | Get a specific user              |
| PATCH  | /users/{id}     | Update role or status            |
| DELETE | /users/{id}     | Permanently delete a user        |

**Query params for GET /users:** `?page=1&limit=20`

### Financial Records (Analyst + Admin for reads, Admin for writes)
| Method | Endpoint          | Description                      |
|--------|-------------------|----------------------------------|
| GET    | /records          | List records with filters        |
| POST   | /records          | Create a new record              |
| GET    | /records/{id}     | Get a specific record            |
| PATCH  | /records/{id}     | Update a record                  |
| DELETE | /records/{id}     | Soft delete a record             |

**Query params for GET /records:**
- `page` — page number (default: 1)
- `limit` — results per page (default: 20, max: 100)
- `type` — filter by `income` or `expense`
- `category` — partial match filter (e.g. `?category=food`)
- `date_from` — start date filter (`YYYY-MM-DD`)
- `date_to` — end date filter (`YYYY-MM-DD`)

**Example:**
```bash
curl "http://localhost:8000/records?type=expense&category=food&page=1&limit=10" \
  -H "Authorization: Bearer <token>"
```

### Dashboard (All authenticated users)
| Method | Endpoint                  | Description                            |
|--------|---------------------------|----------------------------------------|
| GET    | /dashboard/summary        | Total income, expenses, net balance    |
| GET    | /dashboard/by-category    | Totals grouped by category and type    |
| GET    | /dashboard/trends         | Month-by-month income vs expenses      |
| GET    | /dashboard/recent         | Most recent 10 transactions            |

---

## Example curl Commands

**Create a financial record:**
```bash
curl -X POST http://localhost:8000/records \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 5000,
    "type": "income",
    "category": "Salary",
    "date": "2024-04-01",
    "notes": "April salary"
  }'
```

**Get dashboard summary:**
```bash
curl http://localhost:8000/dashboard/summary \
  -H "Authorization: Bearer <token>"
```

**Create a user (admin only):**
```bash
curl -X POST http://localhost:8000/users \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Smith",
    "email": "jane@company.com",
    "password": "secure123",
    "role": "analyst"
  }'
```

---

## Running Tests

```bash
pytest tests/ -v
```

Tests use an in-memory SQLite database — they never touch `finance.db`.

---

## Project Structure

```
finance-backend/
├── app/
│   ├── main.py                  ← FastAPI app, table creation, error handlers
│   ├── database.py              ← SQLAlchemy engine and session factory
│   ├── models/                  ← ORM table definitions
│   │   ├── user.py
│   │   ├── session.py
│   │   └── record.py
│   ├── schemas/                 ← Pydantic request/response validation
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── record.py
│   │   └── dashboard.py
│   ├── routers/                 ← Thin route handlers (no business logic)
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── records.py
│   │   └── dashboard.py
│   ├── services/                ← All business logic lives here
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── record_service.py
│   │   └── dashboard_service.py
│   ├── dependencies/            ← FastAPI dependency injection
│   │   ├── auth.py              ← get_current_user()
│   │   └── rbac.py              ← require_role("admin") factory
│   └── core/
│       ├── config.py            ← App settings
│       └── exceptions.py        ← Custom AppError hierarchy
├── tests/
│   ├── conftest.py              ← Shared fixtures and helpers
│   ├── test_auth.py
│   ├── test_users.py
│   ├── test_records.py
│   └── test_dashboard.py
├── seed.py                      ← Sample data generator
├── requirements.txt
└── README.md
```

---

## Assumptions

These are decisions made where the assignment left room for interpretation:

- **Role hierarchy is flat** — roles are not inherited. A Viewer gets no analyst or admin permissions just because they are "lower". Each role is granted only what is explicitly listed in the permission matrix.
- **Soft delete applies to records only** — users are hard deleted because a deactivated user account already serves the purpose of disabling access without losing the user row.
- **A deleted record is permanently hidden** — once soft deleted, records do not appear in any listing or dashboard query. There is no restore endpoint, though the data remains in the database and could be restored by an admin directly if needed.
- **Session expiry is 8 hours** — after 8 hours of inactivity the session token becomes invalid and the user must log in again. This is configurable in `app/core/config.py`.
- **Passwords use SHA-256 hashing** — in a production system bcrypt or argon2 would be used. SHA-256 is used here to avoid extra dependencies while still demonstrating that passwords are never stored in plain text.
- **An admin cannot delete their own account** — this prevents a situation where the last admin accidentally locks the entire system by deleting themselves.
- **Financial record dates are stored as DATE not DATETIME** — records represent a transaction on a day, not a moment in time. Using DATE avoids timezone confusion and matches how finance data is typically reported.
- **Categories are free-text** — there is no fixed category list. This keeps the system flexible without needing a separate categories table or seeding step.

---

## Design Decisions

**Why session-based auth instead of JWT?**
Sessions are stored in the database, which means logout truly invalidates the token immediately. JWT is stateless — a logged-out JWT is still technically valid until it expires, which creates a security gap. For a finance application where deactivating compromised accounts matters, session-based auth is the more secure choice.

**Why soft delete for records?**
Financial records carry audit value even after they're "removed". Setting `deleted_at` to a timestamp means the data is never lost — it's just invisible to normal queries. This preserves history, supports potential restore functionality, and avoids accidental data loss.

**Why separate routers and services?**
Routers handle HTTP concerns (parsing request params, returning responses). Services contain all business logic (validation, DB queries, error conditions). This separation means business logic can be tested independently of HTTP, and routes stay thin and readable.

**Why raw SQL for dashboard queries?**
Dashboard aggregations (`SUM`, `GROUP BY`, `strftime`) are inherently SQL operations. Writing them as raw SQL is cleaner and more explicit than constructing ORM equivalents, and it demonstrates real data modeling skill. SQLAlchemy's `text()` is used so the queries still go through the managed connection pool.

**Why `require_role` as a factory function?**
`require_role("admin", "analyst")` reads exactly like English at the route level — it's self-documenting. A factory that returns a dependency keeps all RBAC logic in one place and makes adding new roles trivial.

---

## Validation Rules

- `amount` — must be a positive number greater than 0
- `type` — must be exactly `"income"` or `"expense"`
- `category` — cannot be empty or whitespace-only
- `email` — must be a valid email format
- `password` — minimum 6 characters
- `role` — must be one of `"viewer"`, `"analyst"`, `"admin"`
- `status` — must be `"active"` or `"inactive"`

All validation errors return HTTP 422 with a `details` array showing which field failed and why.
