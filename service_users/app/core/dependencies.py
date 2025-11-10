from fastapi import Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.core.security import decode_access_token
from app.core.exceptions import UnauthorizedException, ForbiddenException
from app.models.user import User

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Получает текущего пользователя из JWT токена.
    """
    token = credentials.credentials
    
    # Декодируем токен
    payload = decode_access_token(token)
    if not payload:
        raise UnauthorizedException("Невалидный или истекший токен")
    
    # Получаем user_id из payload
    user_id: str = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Токен не содержит идентификатор пользователя")
    
    # Получаем пользователя из БД
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise UnauthorizedException("Пользователь не найден")
    
    return user


def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Проверяет, что текущий пользователь имеет роль admin.
    """
    if 'admin' not in current_user.roles:
        raise ForbiddenException("Доступ разрешен только администраторам")
    
    return current_user
