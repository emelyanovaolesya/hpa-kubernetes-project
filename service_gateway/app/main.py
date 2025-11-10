from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from app.api.v1.router import api_v1_router
from app.config import settings


app = FastAPI(
    title="API Gateway",
    description="API Gateway для микросервисов Users и Orders",
    version="1.0.0"
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        errors.append(f"{field}: {message}")
    
    error_message = "; ".join(errors)
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "data": None,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": error_message
            }
        }
    )


@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        errors.append(f"{field}: {message}")
    
    error_message = "; ".join(errors)
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "data": None,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": error_message
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "data": None,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "Внутренняя ошибка сервера"
            }
        }
    )


app.include_router(api_v1_router, prefix="/v1")


@app.get("/", tags=["Health"])
async def root():
    return {
        "success": True,
        "data": {
            "service": "API Gateway",
            "version": "1.0.0",
            "status": "running"
        },
        "error": None
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "success": True,
        "data": {
            "status": "healthy",
            "services": {
                "users": settings.SERVICE_USERS_URL,
                "orders": settings.SERVICE_ORDERS_URL
            }
        },
        "error": None
    }
