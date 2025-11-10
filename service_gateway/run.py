"""
Точка входа для запуска API Gateway.
Запускает uvicorn сервер с настройками из config.
"""
import uvicorn
from app.config import settings


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.SERVICE_GATEWAY_HOST,
        port=settings.SERVICE_GATEWAY_PORT,
        reload=True,
        log_level="info"
    )
