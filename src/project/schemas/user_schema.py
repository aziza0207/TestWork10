from pydantic import BaseModel, Field
from typing import Optional


class UserCreate(BaseModel):
    email: Optional[str] = Field(default=None, min_length=5)
    name: Optional[str] = Field(default=None, min_length=1)
    password: Optional[str] = Field(default=None, min_length=6)

    class Config:
        from_attributes = True


class UserRead(BaseModel):
    email: Optional[str] = Field(default=None, min_length=5)
    name: Optional[str] = Field(default=None, min_length=1)

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    user: UserRead
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str