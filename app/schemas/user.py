from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from typing import Optional, Literal

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Literal["viewer", "analyst", "admin"] = "viewer"

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be empty or whitespace.")
        return v.strip()

    @field_validator("password")
    @classmethod
    def password_minimum_length(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters long.")
        return v

class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[Literal["viewer", "analyst", "admin"]] = None
    status: Optional[Literal["active", "inactive"]] = None

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("Name cannot be empty or whitespace.")
        return v.strip() if v else v

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class UserListResponse(BaseModel):
    total: int
    page: int
    limit: int
    users: list[UserResponse]
