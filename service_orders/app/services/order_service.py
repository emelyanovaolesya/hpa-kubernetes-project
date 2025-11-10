from sqlalchemy.orm import Session
from typing import List, Optional
import math
import uuid
from app.models.order import Order, OrderStatus
from app.schemas.order import OrderCreate, OrderUpdate, OrderItem
from app.core.exceptions import NotFoundException, ForbiddenException, ValidationException


class OrderService:
    """Сервис для работы с заказами"""
    
    @staticmethod
    def create_order(db: Session, order_data: OrderCreate, user_id: str) -> Order:
        """
        Создает новый заказ для пользователя.
        """
        total_amount = order_data.calculate_total()
        
        items_dict = [item.model_dump(mode='json') for item in order_data.items]
        
        new_order = Order(
            user_id=uuid.UUID(user_id),
            items=items_dict,
            status=OrderStatus.CREATED,
            total_amount=total_amount
        )
        
        db.add(new_order)
        db.commit()
        db.refresh(new_order)
        
        return new_order
    
    @staticmethod
    def get_order_by_id(db: Session, order_id: str, user_id: str) -> Order:
        """
        Получает заказ по ID с проверкой прав доступа.
        """
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise NotFoundException(f"Заказ с ID '{order_id}' не найден")
        
        if str(order.user_id) != user_id:
            raise ForbiddenException("У вас нет доступа к этому заказу")
        
        return order
    
    @staticmethod
    def get_user_orders(
        db: Session,
        user_id: str,
        page: int = 1,
        size: int = 10,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        status_filter: Optional[str] = None
    ) -> tuple[List[Order], int]:
        """
        Получает список заказов текущего пользователя с пагинацией и сортировкой.
        """
        query = db.query(Order).filter(Order.user_id == user_id)
        
        if status_filter:
            try:
                status_enum = OrderStatus(status_filter)
                query = query.filter(Order.status == status_enum)
            except ValueError:
                raise ValidationException(f"Недопустимый статус: {status_filter}")
        
        if sort_by == "created_at":
            order_column = Order.created_at
        elif sort_by == "updated_at":
            order_column = Order.updated_at
        elif sort_by == "total_amount":
            order_column = Order.total_amount
        else:
            order_column = Order.created_at
        
        if sort_order == "desc":
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())
        
        total = query.count()
        
        offset = (page - 1) * size
        orders = query.offset(offset).limit(size).all()
        
        return orders, total
    
    @staticmethod
    def update_order_status(
        db: Session,
        order_id: str,
        user_id: str,
        update_data: OrderUpdate
    ) -> Order:
        """
        Обновляет статус заказа с проверкой прав доступа.
        """
        order = OrderService.get_order_by_id(db, order_id, user_id)
        
        try:
            new_status = OrderStatus(update_data.status)
        except ValueError:
            raise ValidationException(f"Недопустимый статус: {update_data.status}")
        
        if order.status == OrderStatus.CANCELLED:
            raise ValidationException("Нельзя изменить статус отмененного заказа")
        
        if order.status == OrderStatus.COMPLETED:
            raise ValidationException("Нельзя изменить статус выполненного заказа")
        
        order.status = new_status
        db.commit()
        db.refresh(order)
        
        return order
    
    @staticmethod
    def cancel_order(db: Session, order_id: str, user_id: str) -> Order:
        """
        Отменяет заказ с проверкой прав доступа.
        """
        order = OrderService.get_order_by_id(db, order_id, user_id)
        
        if order.status == OrderStatus.CANCELLED:
            raise ValidationException("Заказ уже отменен")
        
        if order.status == OrderStatus.COMPLETED:
            raise ValidationException("Нельзя отменить выполненный заказ")
        
        order.status = OrderStatus.CANCELLED
        db.commit()
        db.refresh(order)
        
        return order
    
    @staticmethod
    def calculate_total_pages(total: int, size: int) -> int:
        """
        Вычисляет общее количество страниц.
        """
        return math.ceil(total / size) if total > 0 else 0
