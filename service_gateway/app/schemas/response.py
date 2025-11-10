from pydantic import BaseModel
from typing import Any, Optional


class ErrorDetail(BaseModel):
    """Схема для детальной информации об ошибке"""
    code: str
    message: str


class ApiResponse(BaseModel):
    """Единый формат ответа API"""
    success: bool
    data: Optional[Any] = None
    error: Optional[ErrorDetail] = None
