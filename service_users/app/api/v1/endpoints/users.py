from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.schemas.user import UserResponse, UserUpdate, UserListResponse
from app.schemas.response import success_response
from app.services.user_service import UserService
from app.core.dependencies import get_current_user, get_current_admin_user
from app.models.user import User

router = APIRouter()


@router.get(
    "/me",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Получить текущий профиль",
    description="Возвращает профиль текущего авторизованного пользователя"
)
def get_current_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Возвращает профиль текущего пользователя.
    """
    user_response = UserResponse.model_validate(current_user)
    return success_response(user_response.model_dump())


@router.put(
    "/me",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Обновить текущий профиль",
    description="Обновляет профиль текущего авторизованного пользователя"
)
def update_current_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Обновляет профиль текущего пользователя.
    """
    updated_user = UserService.update_user_profile(
        db,
        str(current_user.id),
        update_data
    )
    user_response = UserResponse.model_validate(updated_user)
    return success_response(user_response.model_dump())


@router.get(
    "/",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Получить список всех пользователей (только для админов)",
    description="Возвращает список пользователей с пагинацией и фильтрацией"
)
def get_users_list(
    page: int = Query(1, ge=1, description="Номер страницы"),
    size: int = Query(10, ge=1, le=100, description="Размер страницы"),
    role: Optional[str] = Query(None, description="Фильтр по роли"),
    email: Optional[str] = Query(None, description="Фильтр по email"),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Возвращает список всех пользователей с пагинацией и фильтрацией.
    """
    users, total = UserService.get_users_list(
        db,
        page=page,
        size=size,
        role_filter=role,
        email_filter=email
    )
    
    total_pages = UserService.calculate_total_pages(total, size)
    
    user_list_response = UserListResponse(
        users=[UserResponse.model_validate(user) for user in users],
        total=total,
        page=page,
        size=size,
        total_pages=total_pages
    )
    
    return success_response(user_list_response.model_dump())
