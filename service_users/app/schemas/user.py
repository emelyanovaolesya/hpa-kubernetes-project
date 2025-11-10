from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List, Literal
from datetime import datetime
import uuid


# Типы ролей
RoleType = Literal['admin', 'client']


class UserBase(BaseModel):
    """Базовая схема пользователя"""
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)


class UserCreate(UserBase):
    """Схема для создания пользователя (регистрация)"""
    password: str = Field(..., min_length=8, max_length=100)
    roles: List[RoleType] = Field(default=['client'])
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Валидация пароля: минимум 8 символов, содержит буквы и цифры"""
        if len(v) < 8:
            raise ValueError('Пароль должен содержать минимум 8 символов')
        if not any(c.isdigit() for c in v):
            raise ValueError('Пароль должен содержать хотя бы одну цифру')
        if not any(c.isalpha() for c in v):
            raise ValueError('Пароль должен содержать хотя бы одну букву')
        return v
    
    @field_validator('roles')
    @classmethod
    def validate_roles(cls, v: List[str]) -> List[str]:
        """Валидация ролей"""
        allowed_roles = {'admin', 'client'}
        for role in v:
            if role not in allowed_roles:
                raise ValueError(f'Недопустимая роль: {role}. Доступные роли: {allowed_roles}')
        if not v:
            raise ValueError('Необходимо указать хотя бы одну роль')
        return v


class UserUpdate(BaseModel):
    """Схема для обновления профиля пользователя"""
    name: str | None = Field(None, min_length=1, max_length=100)
    password: str | None = Field(None, min_length=8, max_length=100)
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str | None) -> str | None:
        """Валидация пароля при обновлении"""
        if v is None:
            return v
        if len(v) < 8:
            raise ValueError('Пароль должен содержать минимум 8 символов')
        if not any(c.isdigit() for c in v):
            raise ValueError('Пароль должен содержать хотя бы одну цифру')
        if not any(c.isalpha() for c in v):
            raise ValueError('Пароль должен содержать хотя бы одну букву')
        return v


class UserResponse(UserBase):
    """Схема для возврата информации о пользователе"""
    id: uuid.UUID
    roles: List[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Схема для авторизации пользователя"""
    email: EmailStr
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    """Схема для возврата JWT токена"""
    access_token: str
    token_type: str = "bearer"


class UserListResponse(BaseModel):
    """Схема для возврата списка пользователей с пагинацией"""
    users: List[UserResponse]
    total: int
    page: int
    size: int
    total_pages: int
