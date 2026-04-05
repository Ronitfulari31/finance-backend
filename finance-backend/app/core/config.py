import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATABASE_URL = f"sqlite:///{BASE_DIR}/finance.db"

SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY", "change-this-in-production-please")
SESSION_MAX_AGE_SECONDS = 60 * 60 * 8  # 8 hours

# App metadata
APP_TITLE = "Finance Data Processing API"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = """
A backend API for managing financial records with role-based access control.

## Roles
- **Viewer** — Read-only access to dashboard summaries
- **Analyst** — Can view and filter financial records + dashboard
- **Admin** — Full access: user management, record CRUD, all dashboards

## Authentication
This API uses session-based authentication. Login via `POST /auth/login`
to receive a session token, then pass it in the `Authorization: Bearer <token>` header.
"""
