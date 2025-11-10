from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.core.security import hash_password, verify_password, create_access_token
from app.core.exceptions import ConflictException, UnauthorizedException


class AuthService:
    """Сервис для работы с аутентификацией и авторизацией"""
    
    @staticmethod
    def register_user(db: Session, user_data: UserCreate) -> User:
        """
        Регистрирует нового пользователя.
        """
        # Проверяем, существует ли пользователь с таким email
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise ConflictException(
                f"Пользователь с email '{user_data.email}' уже существует"
            )
        
        hashed_password = hash_password(user_data.password)
        
        new_user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            name=user_data.name,
            roles=user_data.roles
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return new_user
    
    @staticmethod
    def authenticate_user(db: Session, login_data: UserLogin) -> str:
        """
        Аутентифицирует пользователя и возвращает JWT токен.
        """
        user = db.query(User).filter(User.email == login_data.email).first()
        if not user:
            raise UnauthorizedException("Неверный email или пароль")
        
        if not verify_password(login_data.password, user.hashed_password):
            raise UnauthorizedException("Неверный email или пароль")
        
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "roles": user.roles}
        )
        
        return access_token
