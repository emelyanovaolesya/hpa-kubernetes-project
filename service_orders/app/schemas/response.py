from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel

DataT = TypeVar('DataT')


class ErrorDetail(BaseModel):
    """Схема для детальной информации об ошибке"""
    code: str
    message: str


class ApiResponse(BaseModel, Generic[DataT]):
    """
    Единый формат ответа для всех API endpoints.
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
