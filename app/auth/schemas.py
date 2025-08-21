from pydantic import BaseModel
from typing import Optional, Dict

class LoginRequest(BaseModel):
    email: str
    password: str


class RoleResponse(BaseModel):
    # id: int
    code: str
    name: str

class UserResponse(BaseModel):
    # id: int
    email: str
    username: str
    fullName: Optional[str]

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    role: Optional[RoleResponse]
    user: UserResponse