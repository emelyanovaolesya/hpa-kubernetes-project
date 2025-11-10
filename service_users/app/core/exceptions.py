class AppException(Exception):
    """Базовый класс для всех кастомных исключений приложения"""
    
    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class UnauthorizedException(AppException):
    """Исключение для неавторизованных запросов"""
    
    def __init__(self, message: str = "Не авторизован"):
        super().__init__(
            code="UNAUTHORIZED",
            message=message,
            status_code=401
        )


class ForbiddenException(AppException):
    """Исключение для запрещенных действий"""
    
    def __init__(self, message: str = "Доступ запрещен"):
        super().__init__(
            code="FORBIDDEN",
            message=message,
            status_code=403
        )


class NotFoundException(AppException):
    """Исключение для не найденных ресурсов"""
    
    def __init__(self, message: str = "Ресурс не найден"):
        super().__init__(
            code="NOT_FOUND",
            message=message,
            status_code=404
        )


class ConflictException(AppException):
    """Исключение для конфликтов (например, пользователь уже существует)"""
    
    def __init__(self, message: str = "Конфликт данных"):
        super().__init__(
            code="CONFLICT",
            message=message,
            status_code=409
        )


class ValidationException(AppException):
    """Исключение для ошибок валидации"""
    
    def __init__(self, message: str = "Ошибка валидации"):
        super().__init__(
            code="VALIDATION_ERROR",
            message=message,
            status_code=422
        )
