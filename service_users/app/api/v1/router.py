from fastapi import APIRouter
from app.api.v1.endpoints import auth, users

# Создаем роутер для версии v1 API
api_v1_router = APIRouter()

# Подключаем роутеры endpoints
api_v1_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

api_v1_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"]
)
