from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from fastapi import UploadFile, File, Form


# Pydantic schema for validation of User Fields
class User(BaseModel):
    id: Optional[UUID] = None
    name: str
    username: str
    email: Optional[str] = None
    phone: Optional[str] = None
    password: str
    is_authenticated: bool = False

    class Config:
        form_attributes = True


class UserResponse(BaseModel):
    id: str
    name: str
    username: str
    email: str
    phone: str
    is_authenticated: bool

    class Config:
        form_attributes = True


class UserCreate(BaseModel):
    id: Optional[UUID] = None
    name: str
    username: str
    email: Optional[str] = None
    phone: Optional[str] = None
    password: str
    is_authenticated: bool = False

    class Config:
        form_attributes = True


class Token(BaseModel):
    data: Optional[dict]
    access_token: Optional[str]
    token_type: Optional[str]
    status_code: Optional[int]
    message: str


# Model for data that login route receives
class LoginRequest(BaseModel):
    username: str
    password: str


# Model for change password feature
class ChangePassword(BaseModel):
    old_password: str
    new_password: str


class TokenData(BaseModel):
    username: str | None = None
