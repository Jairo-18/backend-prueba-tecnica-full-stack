from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    username: str
    fullName: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role_type_id: Optional[int] = 1

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    fullName: Optional[str] = None
    password: Optional[str] = None
    role_type_id: Optional[int] = None

class UserResponse(UserBase):
    id: int
    role_type_id: int
    class Config:
        from_attributes = True  # para usar con SQLAlchemy ORM
