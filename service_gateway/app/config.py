from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    """Настройки API Gateway"""
    
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    
    SERVICE_GATEWAY_HOST: str = "localhost"
    SERVICE_GATEWAY_PORT: int = 8000
    
    SERVICE_USERS_URL: str = "http://localhost:8002"
    SERVICE_ORDERS_URL: str = "http://localhost:8001"
    
    class Config:
        env_file = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
        env_file_encoding = "utf-8"
        extra = 'ignore'
        case_sensitive = True


settings = Settings()
