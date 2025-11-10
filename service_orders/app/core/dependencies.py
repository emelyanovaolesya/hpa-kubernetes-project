from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict
from app.core.security import decode_access_token
from app.core.exceptions import UnauthorizedException

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict:
    """
    Получает текущего пользователя из JWT токена.
    Не обращается к базе данных, только валидирует токен.
    """
    token = credentials.credentials
    
    payload = decode_access_token(token)
    if not payload:
        raise UnauthorizedException("Невалидный или истекший токен")
    
    user_id: str = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Токен не содержит идентификатор пользователя")
    
    email: str = payload.get("email")
    roles: list = payload.get("roles", [])
    
    return {
        "user_id": user_id,
        "email": email,
        "roles": roles
    }
