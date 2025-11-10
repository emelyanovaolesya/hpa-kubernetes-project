from sqlalchemy import Column, String, DateTime, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from app.database import Base


class User(Base):
    """
    Модель пользователя для хранения в базе данных PostgreSQL.
    
    Поля:
    - id: UUID - уникальный идентификатор пользователя
    - email: str - электронная почта (уникальная)
    - hashed_password: str - хэшированный пароль
    - name: str - имя пользователя
    - roles: List[str] - массив ролей ['admin', 'client']
    - created_at: datetime - дата создания
    - updated_at: datetime - дата последнего обновления
    """
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    roles = Column(ARRAY(String), nullable=False, default=['client'])
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, name={self.name})>"
