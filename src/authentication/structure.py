from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from uuid import UUID
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    full_name: str = Field(..., example="Shubham Pasari")
    password: str = Field(..., min_length=8, example="P@ss1092")
    roles: Optional[list] = Field([], example="['TASK_CREATE', 'TASK_VIEW', 'TASK_DELETE', 'TASK_EDIT']")

class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True
    
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    refresh_token: str