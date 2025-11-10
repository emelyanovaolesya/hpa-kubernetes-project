from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    """Настройки приложения, загружаемые из переменных окружения"""
    
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    SERVICE_ORDERS_HOST: str = "localhost"
    SERVICE_ORDERS_PORT: int = 8001
    
    @property
    def DATABASE_URL(self) -> str:
        """Формирует URL для подключения к PostgreSQL"""
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    class Config:
        env_file = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
        env_file_encoding = "utf-8"
        extra='ignore'
        case_sensitive = True


settings = Settings()
