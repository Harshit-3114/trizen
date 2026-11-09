from pydantic import BaseModel, EmailStr


class MemberAdd(BaseModel):
    email: EmailStr


class MemberResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str  # "admin" for event owner, else "member"
