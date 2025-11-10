from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel

# TypeVar для Generic типов
DataT = TypeVar('DataT')


class ErrorDetail(BaseModel):
    """Схема для детальной информации об ошибке"""
    code: str
    message: str


class ApiResponse(BaseModel, Generic[DataT]):
    """
    Единый формат ответа для всех API endpoints.
    
    Поля:
    - success: bool - успешность операции
    - data: DataT | None - данные ответа (Generic тип)
    - error: ErrorDetail | None - информация об ошибке
    """
    success: bool
    data: Optional[DataT] = None
    error: Optional[ErrorDetail] = None
    
    class Config:
        from_attributes = True


def success_response(data: Any) -> dict:
    """Создает успешный ответ"""
    return {
        "success": True,
        "data": data,
        "error": None
    }


def error_response(code: str, message: str) -> dict:
    """Создает ответ с ошибкой"""
    return {
        "success": False,
        "data": None,
        "error": {
            "code": code,
            "message": message
        }
    }
