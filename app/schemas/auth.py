from pydantic import BaseModel, EmailStr, Field

from app.schemas.users import UserListItem


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=6, max_length=128)


class VerifyPassword(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)


class UserCapabilities(BaseModel):
    can_view_all_employees: bool = False
    can_manage_employees: bool = False
    can_manage_documents: bool = False
    can_manage_employee_files: bool = False
    can_manage_notifications: bool = False
    can_manage_requests: bool = False
    can_manage_all_requests: bool = False
    can_manage_assigned_requests: bool = False
    can_manage_vacations: bool = False
    can_upload_payslips: bool = False
    can_track_signatures: bool = False
    can_sign_payslips: bool = False


class AuthMeResponse(UserListItem):
    # Others
    capabilities: UserCapabilities
