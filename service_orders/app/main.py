from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from app.api.v1.router import api_v1_router
from app.core.exceptions import AppException
from app.schemas.response import error_response
from app.database import init_db
from app.config import settings


app = FastAPI(
    title="Orders Service API",
    description="Сервис управления заказами с JWT аутентификацией",
    version="1.0.0"
)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(exc.code, exc.message)
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
        content=error_response("VALIDATION_ERROR", error_message)
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
        content=error_response("VALIDATION_ERROR", error_message)
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response(
            "INTERNAL_SERVER_ERROR",
            "Внутренняя ошибка сервера"
        )
    )


app.include_router(api_v1_router, prefix="/v1")


@app.on_event("startup")
async def startup_event():
    init_db()


@app.get("/", tags=["Health"])
async def root():
    return {
        "success": True,
        "data": {
            "service": "Orders Service",
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
            "status": "healthy"
        },
        "error": None
    }
