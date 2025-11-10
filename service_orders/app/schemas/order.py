from pydantic import BaseModel, Field, field_validator
from typing import List, Literal
from datetime import datetime
from decimal import Decimal
import uuid
from app.models.order import OrderStatus


class OrderItem(BaseModel):
    """Схема товара в заказе"""
    name: str = Field(..., min_length=1, max_length=200, description="Название товара")
    amount: int = Field(..., gt=0, description="Количество товара")
    description: str = Field(..., min_length=1, max_length=500, description="Описание товара")
    price: Decimal = Field(..., gt=0, description="Цена товара")
    
    @field_validator('price')
    @classmethod
    def validate_price(cls, v: Decimal) -> Decimal:
        """Валидация цены"""
        if v <= 0:
            raise ValueError('Цена должна быть больше 0')
        # Ограничиваем до 2 знаков после запятой
        return round(v, 2)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Laptop",
                "amount": 2,
                "description": "High-performance laptop",
                "price": 1200.50
            }
        }


class OrderCreate(BaseModel):
    """Схема для создания заказа"""
    items: List[OrderItem] = Field(..., min_length=1, description="Список товаров")
    
    @field_validator('items')
    @classmethod
    def validate_items(cls, v: List[OrderItem]) -> List[OrderItem]:
        """Валидация списка товаров"""
        if not v:
            raise ValueError('Заказ должен содержать хотя бы один товар')
        return v
    
    def calculate_total(self) -> Decimal:
        """Вычисляет общую сумму заказа"""
        return sum(item.price * item.amount for item in self.items)


class OrderUpdate(BaseModel):
    """Схема для обновления статуса заказа"""
    status: Literal["CREATED", "IN_PROGRESS", "COMPLETED", "CANCELLED"] = Field(..., description="Новый статус заказа")


class OrderResponse(BaseModel):
    """Схема для возврата информации о заказе"""
    id: uuid.UUID
    user_id: uuid.UUID
    items: List[OrderItem]
    status: str
    total_amount: Decimal
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174001",
                "items": [
                    {
                        "name": "Laptop",
                        "amount": 2,
                        "description": "High-performance laptop",
                        "price": 1200.50
                    }
                ],
                "status": "CREATED",
                "total_amount": 2401.00,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        }


class OrderListResponse(BaseModel):
    """Схема для возврата списка заказов с пагинацией"""
    orders: List[OrderResponse]
    total: int
    page: int
    size: int
    total_pages: int
