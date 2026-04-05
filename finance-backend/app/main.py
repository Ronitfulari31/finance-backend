from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from app.core.config import APP_TITLE, APP_VERSION, APP_DESCRIPTION
from app.database import engine
from app.models import User, Session, FinancialRecord 
from app.database import Base
from app.routers import auth, users, records, dashboard

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    docs_url="/docs",      
    redoc_url="/redoc",     
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=APP_TITLE,
        version=APP_VERSION,
        description=APP_DESCRIPTION,
        routes=app.routes,
    )
    schema["components"]["securitySchemes"] = {
        "HTTPBearer": {
            "type": "http",
            "scheme": "bearer",
        }
    }
    for path in schema.get("paths", {}).values():
        for operation in path.values():
            operation["security"] = [{"HTTPBearer": []}]
    app.openapi_schema = schema
    return app.openapi_schema

app.openapi = custom_openapi

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(records.router)
app.include_router(dashboard.router)

@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"] if loc != "body")
        errors.append({"field": field, "message": error["msg"]})

    return JSONResponse(
        status_code=422,
        content={"success": False, "error": "Validation failed.", "details": errors}
    )

@app.get("/", tags=["Health"], summary="Health check")
def root():
    return {
        "status": "ok",
        "app": APP_TITLE,
        "version": APP_VERSION,
        "docs": "/docs"
    }