from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserListItem(BaseModel):
    user_id: str
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    is_verified: bool


class UserDetail(UserListItem):
    created_at: datetime
    updated_at: datetime


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    is_verified: bool = False


class UserUpdate(BaseModel):
    username: str | None = Field(None, min_length=3, max_length=100)
    email: EmailStr | None = None
    first_name: str | None = Field(None, max_length=100)
    last_name: str | None = Field(None, max_length=100)
    is_verified: bool | None = None
