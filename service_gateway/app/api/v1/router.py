from fastapi import APIRouter
from app.api.v1.endpoints import users, orders

api_v1_router = APIRouter()

# Подключаем роутеры с префиксами
api_v1_router.include_router(
    users.router,
    tags=["Users & Auth"]
)

api_v1_router.include_router(
    orders.router,
    prefix="/orders",
    tags=["Orders"]
)
