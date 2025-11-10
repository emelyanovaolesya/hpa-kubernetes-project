import httpx
from typing import Optional, Dict, Any
from fastapi import HTTPException
from app.config import settings


class ServiceProxy:
    """Клиент для проксирования запросов к микросервисам"""
    
    def __init__(self):
        self.timeout = httpx.Timeout(30.0, connect=10.0)
    
    async def forward_request(
        self,
        service_url: str,
        path: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        query_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Пересылает запрос к микросервису.
        
        Args:
            service_url: URL сервиса
            path: Путь endpoint
            method: HTTP метод
            headers: Заголовки запроса
            json_data: JSON данные для отправки
            query_params: Query параметры
        
        Returns:
            Ответ от сервиса
        """
        url = f"{service_url}/{path.lstrip('/')}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=json_data,
                    params=query_params
                )
                
                # Проверяем успешность запроса
                if response.status_code >= 400:
                    # Возвращаем ошибку от сервиса
                    try:
                        error_data = response.json()
                        raise HTTPException(
                            status_code=response.status_code,
                            detail=error_data
                        )
                    except ValueError:
                        raise HTTPException(
                            status_code=response.status_code,
                            detail=response.text
                        )
                
                return response.json()
                
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503,
                detail={
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "SERVICE_UNAVAILABLE",
                        "message": f"Сервис недоступен: {str(e)}"
                    }
                }
            )
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=504,
                detail={
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "GATEWAY_TIMEOUT",
                        "message": "Превышено время ожидания ответа от сервиса"
                    }
                }
            )


# Глобальный экземпляр proxy
proxy = ServiceProxy()
