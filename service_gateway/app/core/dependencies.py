from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict
from app.core.security import decode_access_token

security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict]:
    """
    Получает текущего пользователя из JWT токена (опционально).
    Используется для незащищенных эндпоинтов.
    """
    if not credentials:
        return None
    
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if not payload:
        return None
    
    return {
        "user_id": payload.get("sub"),
        "email": payload.get("email"),
        "roles": payload.get("roles", [])
    }


def get_required_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict:
    """
    Получает текущего пользователя из JWT токена (обязательно).
    Используется для защищенных эндпоинтов.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен авторизации не предоставлен"
        )
    
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный или истекший токен"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен не содержит идентификатор пользователя"
        )
    
    return {
        "user_id": user_id,
        "email": payload.get("email"),
        "roles": payload.get("roles", []),
        "token": token  # Сохраняем токен для проксирования
    }
