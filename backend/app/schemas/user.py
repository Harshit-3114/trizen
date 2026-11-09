from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = ""


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=128)
    role: str = Field(default="member", pattern="^(admin|member)$")


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
    is_active: bool


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None
