"""
Точка входа для запуска Orders Service.
Запускает uvicorn сервер с настройками из config.
"""
import uvicorn
from app.config import settings


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.SERVICE_ORDERS_HOST,
        port=settings.SERVICE_ORDERS_PORT,
        reload=True,
        log_level="info"
    )
