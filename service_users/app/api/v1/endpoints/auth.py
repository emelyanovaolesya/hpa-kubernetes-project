from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.schemas.response import success_response
from app.services.auth_service import AuthService

router = APIRouter()


@router.post(
    "/register",
    response_model=None,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
    description="Создает нового пользователя с валидацией всех полей"
)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Регистрирует нового пользователя.
    """
    user = AuthService.register_user(db, user_data)
    user_response = UserResponse.model_validate(user)
    return success_response(user_response.model_dump())


@router.post(
    "/login",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Авторизация пользователя",
    description="Авторизует пользователя и возвращает JWT токен"
)
def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Авторизует пользователя и возвращает JWT access token.
    """
    access_token = AuthService.authenticate_user(db, login_data)
    token_response = TokenResponse(access_token=access_token)
    return success_response(token_response.model_dump())
