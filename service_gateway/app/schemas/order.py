from pydantic import BaseModel, Field
from typing import List, Literal
from datetime import datetime
from decimal import Decimal
import uuid


class OrderItem(BaseModel):
    """Схема товара в заказе"""
    name: str = Field(..., min_length=1, max_length=200, description="Название товара")
    amount: int = Field(..., gt=0, description="Количество товара")
    description: str = Field(..., min_length=1, max_length=500, description="Описание товара")
    price: Decimal = Field(..., gt=0, description="Цена товара")


class OrderCreate(BaseModel):
    """Схема для создания заказа"""
    items: List[OrderItem] = Field(..., min_length=1, description="Список товаров")


class OrderUpdate(BaseModel):
    """Схема для обновления статуса заказа"""
    status: Literal["CREATED", "IN_PROGRESS", "COMPLETED", "CANCELLED"] = Field(..., description="Новый статус заказа")


class OrderResponse(BaseModel):
    """Схема ответа с данными заказа"""
    id: uuid.UUID
    user_id: uuid.UUID
    items: List[OrderItem]
    status: str
    total_amount: Decimal
    created_at: datetime
    updated_at: datetime


class OrderListResponse(BaseModel):
    """Схема ответа со списком заказов"""
    orders: List[OrderResponse]
    total: int
    page: int
    size: int
    total_pages: int
