"""
Точка входа для запуска User Service.
Запускает uvicorn сервер с настройками из config.
"""
import uvicorn
from app.config import settings


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.SERVICE_USERS_HOST,
        port=settings.SERVICE_USERS_PORT,
        reload=True,  # Автоперезагрузка при изменении кода (для разработки)
        log_level="info"
    )
