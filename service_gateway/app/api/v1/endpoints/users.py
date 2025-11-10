from fastapi import APIRouter, Depends, Query, status
from typing import Dict, Optional
from app.schemas.user import UserCreate, UserLogin, UserUpdate
from app.schemas.response import ApiResponse
from app.core.dependencies import get_required_user
from app.core.proxy import proxy
from app.config import settings

router = APIRouter()


@router.post(
    "/auth/register",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiResponse,
    summary="Регистрация нового пользователя",
    description="Создает нового пользователя с валидацией всех полей",
    responses={
        201: {
            "description": "Пользователь успешно зарегистрирован",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "email": "user@example.com",
                            "name": "John Doe",
                            "roles": ["client"],
                            "created_at": "2024-01-01T00:00:00",
                            "updated_at": "2024-01-01T00:00:00"
                        },
                        "error": None
                    }
                }
            }
        },
        422: {"description": "Ошибка валидации данных"},
        409: {"description": "Пользователь с таким email уже существует"}
    }
)
async def register(user_data: UserCreate):
    """
    Регистрирует нового пользователя.
    
    - **email**: Email пользователя (должен быть валидным и уникальным)
    - **password**: Пароль (минимум 8 символов, должен содержать буквы и цифры)
    - **name**: Имя пользователя
    - **roles**: Список ролей (по умолчанию ['client'])
    """
    return await proxy.forward_request(
        service_url=settings.SERVICE_USERS_URL,
        path="v1/auth/register",
        method="POST",
        json_data=user_data.model_dump()
    )


@router.post(
    "/auth/login",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse,
    summary="Авторизация пользователя",
    description="Авторизует пользователя и возвращает JWT токен",
    responses={
        200: {
            "description": "Успешная авторизация",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                            "token_type": "bearer"
                        },
                        "error": None
                    }
                }
            }
        },
        401: {"description": "Неверный email или пароль"},
        422: {"description": "Ошибка валидации данных"}
    }
)
async def login(login_data: UserLogin):
    """
    Авторизует пользователя и возвращает JWT access token.
    
    - **email**: Email пользователя
    - **password**: Пароль пользователя
    """
    return await proxy.forward_request(
        service_url=settings.SERVICE_USERS_URL,
        path="v1/auth/login",
        method="POST",
        json_data=login_data.model_dump()
    )


@router.get(
    "/users/me",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse,
    summary="Получить текущий профиль",
    description="Возвращает профиль текущего авторизованного пользователя",
    responses={
        200: {
            "description": "Профиль пользователя",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "email": "user@example.com",
                            "name": "John Doe",
                            "roles": ["client"],
                            "created_at": "2024-01-01T00:00:00",
                            "updated_at": "2024-01-01T00:00:00"
                        },
                        "error": None
                    }
                }
            }
        },
        401: {"description": "Не авторизован"}
    }
)
async def get_current_profile(
    current_user: Dict = Depends(get_required_user)
):
    """
    Возвращает профиль текущего пользователя.
    
    Требуется авторизация (Bearer токен в заголовке Authorization).
    """
    return await proxy.forward_request(
        service_url=settings.SERVICE_USERS_URL,
        path="v1/users/me",
        method="GET",
        headers={"Authorization": f"Bearer {current_user.get('token', '')}"}
    )


@router.put(
    "/users/me",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse,
    summary="Обновить текущий профиль",
    description="Обновляет профиль текущего авторизованного пользователя",
    responses={
        200: {
            "description": "Профиль успешно обновлен",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "email": "user@example.com",
                            "name": "Jane Doe",
                            "roles": ["client"],
                            "created_at": "2024-01-01T00:00:00",
                            "updated_at": "2024-01-01T00:10:00"
                        },
                        "error": None
                    }
                }
            }
        },
        401: {"description": "Не авторизован"},
        422: {"description": "Ошибка валидации данных"}
    }
)
async def update_current_profile(
    update_data: UserUpdate,
    current_user: Dict = Depends(get_required_user)
):
    """
    Обновляет профиль текущего пользователя.
    
    - **name**: Новое имя (опционально)
    - **password**: Новый пароль (опционально, минимум 8 символов)
    
    Требуется авторизация (Bearer токен в заголовке Authorization).
    """
    return await proxy.forward_request(
        service_url=settings.SERVICE_USERS_URL,
        path="v1/users/me",
        method="PUT",
        headers={"Authorization": f"Bearer {current_user.get('token', '')}"},
        json_data=update_data.model_dump(exclude_none=True)
    )


@router.get(
    "/users/",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse,
    summary="Получить список всех пользователей (только для админов)",
    description="Возвращает список пользователей с пагинацией и фильтрацией",
    responses={
        200: {
            "description": "Список пользователей",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "users": [
                                {
                                    "id": "123e4567-e89b-12d3-a456-426614174000",
                                    "email": "user@example.com",
                                    "name": "John Doe",
                                    "roles": ["client"],
                                    "created_at": "2024-01-01T00:00:00",
                                    "updated_at": "2024-01-01T00:00:00"
                                }
                            ],
                            "total": 100,
                            "page": 1,
                            "size": 10,
                            "total_pages": 10
                        },
                        "error": None
                    }
                }
            }
        },
        401: {"description": "Не авторизован"},
        403: {"description": "Доступ запрещен (только для администраторов)"}
    }
)
async def get_users_list(
    page: int = Query(1, ge=1, description="Номер страницы"),
    size: int = Query(10, ge=1, le=100, description="Размер страницы"),
    role: Optional[str] = Query(None, description="Фильтр по роли"),
    email: Optional[str] = Query(None, description="Фильтр по email"),
    current_user: Dict = Depends(get_required_user)
):
    """
    Возвращает список всех пользователей с пагинацией и фильтрацией.
    
    - **page**: Номер страницы (начиная с 1)
    - **size**: Размер страницы (1-100)
    - **role**: Фильтр по роли (опционально)
    - **email**: Фильтр по email (частичное совпадение, опционально)
    
    Требуется авторизация с ролью 'admin'.
    """
    query_params = {"page": page, "size": size}
    if role:
        query_params["role"] = role
    if email:
        query_params["email"] = email
    
    return await proxy.forward_request(
        service_url=settings.SERVICE_USERS_URL,
        path="v1/users/all",
        method="GET",
        headers={"Authorization": f"Bearer {current_user.get('token', '')}"},
        query_params=query_params
    )
