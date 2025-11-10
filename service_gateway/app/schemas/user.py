from pydantic import BaseModel, EmailStr, Field
from typing import List
from datetime import datetime
import uuid


class UserCreate(BaseModel):
    """Схема для регистрации пользователя"""
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=8, max_length=100)
    roles: List[str] = Field(default=['client'])


class UserLogin(BaseModel):
    """Схема для авторизации пользователя"""
    email: EmailStr
    password: str = Field(..., min_length=1)


class UserUpdate(BaseModel):
    """Схема для обновления профиля пользователя"""
    name: str | None = Field(None, min_length=1, max_length=100)
    password: str | None = Field(None, min_length=8, max_length=100)


class UserResponse(BaseModel):
    """Схема ответа с данными пользователя"""
    id: uuid.UUID
    email: str
    name: str
    roles: List[str]
    created_at: datetime
    updated_at: datetime


class TokenResponse(BaseModel):
    """Схема ответа с JWT токеном"""
    access_token: str
    token_type: str = "bearer"


class UserListResponse(BaseModel):
    """Схема ответа со списком пользователей"""
    users: List[UserResponse]
    total: int
    page: int
    size: int
    total_pages: int
