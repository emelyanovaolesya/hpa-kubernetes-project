from sqlalchemy import Column, String, DateTime, Numeric, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid
import enum
from app.database import Base


class OrderStatus(str, enum.Enum):
    """Статусы заказа"""
    CREATED = "CREATED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class Order(Base):
    """
    Модель заказа для хранения в базе данных PostgreSQL.
    
    Поля:
    - id: UUID - уникальный идентификатор заказа
    - user_id: UUID - идентификатор пользователя
    - items: JSONB - массив товаров [{name, amount, description, price}]
    - status: OrderStatus - статус заказа
    - total_amount: Decimal - итоговая сумма
    - created_at: datetime - дата создания
    - updated_at: datetime - дата последнего обновления
    """
    
    __tablename__ = "orders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    items = Column(JSONB, nullable=False)
    status = Column(
        SQLEnum(OrderStatus, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        default=OrderStatus.CREATED
    )
    total_amount = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Order(id={self.id}, user_id={self.user_id}, status={self.status})>"
