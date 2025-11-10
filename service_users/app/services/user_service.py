from sqlalchemy.orm import Session
from typing import List, Optional
import math
from app.models.user import User
from app.schemas.user import UserUpdate
from app.core.security import hash_password
from app.core.exceptions import NotFoundException


class UserService:
    """Сервис для работы с пользователями"""
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> User:
        """
        Получает пользователя по ID.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundException(f"Пользователь с ID '{user_id}' не найден")
        return user
    
    @staticmethod
    def update_user_profile(
        db: Session,
        user_id: str,
        update_data: UserUpdate
    ) -> User:
        """
        Обновляет профиль пользователя.
        """
        user = UserService.get_user_by_id(db, user_id)
        
        # Обновляем только переданные поля
        if update_data.name is not None:
            user.name = update_data.name
        
        if update_data.password is not None:
            user.hashed_password = hash_password(update_data.password)
        
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def get_users_list(
        db: Session,
        page: int = 1,
        size: int = 10,
        role_filter: Optional[str] = None,
        email_filter: Optional[str] = None
    ) -> tuple[List[User], int]:
        """
        Получает список пользователей с пагинацией и фильтрацией.
        """
        query = db.query(User)
        
        # Применяем фильтры
        if role_filter:
            query = query.filter(User.roles.contains([role_filter]))
        
        if email_filter:
            query = query.filter(User.email.ilike(f"%{email_filter}%"))
        
        total = query.count()
        
        offset = (page - 1) * size
        users = query.offset(offset).limit(size).all()
        
        return users, total
    
    @staticmethod
    def calculate_total_pages(total: int, size: int) -> int:
        """
        Вычисляет общее количество страниц.
        """
        return math.ceil(total / size) if total > 0 else 0
