from fastapi import APIRouter, Depends, Query, status
from typing import Dict, Optional
from app.schemas.order import OrderCreate, OrderUpdate
from app.schemas.response import ApiResponse
from app.core.dependencies import get_required_user
from app.core.proxy import proxy
from app.config import settings

router = APIRouter()


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiResponse,
    summary="Создать новый заказ",
    description="Создает новый заказ для текущего авторизованного пользователя",
    responses={
        201: {
            "description": "Заказ успешно создан",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "user_id": "123e4567-e89b-12d3-a456-426614174001",
                            "items": [
                                {
                                    "name": "Laptop",
                                    "amount": 2,
                                    "description": "High-performance laptop",
                                    "price": 1200.50
                                }
                            ],
                            "status": "CREATED",
                            "total_amount": 2401.00,
                            "created_at": "2024-01-01T00:00:00",
                            "updated_at": "2024-01-01T00:00:00"
                        },
                        "error": None
                    }
                }
            }
        },
        401: {"description": "Не авторизован"},
        422: {"description": "Ошибка валидации данных"}
    }
)
async def create_order(
    order_data: OrderCreate,
    current_user: Dict = Depends(get_required_user)
):
    """
    Создает новый заказ.
    
    - **items**: Список товаров (минимум 1)
      - **name**: Название товара
      - **amount**: Количество (больше 0)
      - **description**: Описание товара
      - **price**: Цена товара (больше 0)
    
    Требуется авторизация (Bearer токен в заголовке Authorization).
    """
    return await proxy.forward_request(
        service_url=settings.SERVICE_ORDERS_URL,
        path="v1/orders/create",
        method="POST",
        headers={"Authorization": f"Bearer {current_user['token']}"},
        json_data=order_data.model_dump(mode='json')
    )


@router.get(
    "/{order_id}",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse,
    summary="Получить заказ по ID",
    description="Возвращает информацию о заказе по его идентификатору",
    responses={
        200: {
            "description": "Информация о заказе",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "user_id": "123e4567-e89b-12d3-a456-426614174001",
                            "items": [
                                {
                                    "name": "Laptop",
                                    "amount": 2,
                                    "description": "High-performance laptop",
                                    "price": 1200.50
                                }
                            ],
                            "status": "CREATED",
                            "total_amount": 2401.00,
                            "created_at": "2024-01-01T00:00:00",
                            "updated_at": "2024-01-01T00:00:00"
                        },
                        "error": None
                    }
                }
            }
        },
        401: {"description": "Не авторизован"},
        403: {"description": "Доступ запрещен (не ваш заказ)"},
        404: {"description": "Заказ не найден"}
    }
)
async def get_order(
    order_id: str,
    current_user: Dict = Depends(get_required_user)
):
    """
    Получает заказ по ID с проверкой прав доступа.
    
    - **order_id**: UUID заказа
    
    Требуется авторизация (Bearer токен в заголовке Authorization).
    """
    return await proxy.forward_request(
        service_url=settings.SERVICE_ORDERS_URL,
        path=f"v1/orders/{order_id}",
        method="GET",
        headers={"Authorization": f"Bearer {current_user['token']}"}
    )


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse,
    summary="Получить список заказов текущего пользователя",
    description="Возвращает список заказов с пагинацией, сортировкой и фильтрацией",
    responses={
        200: {
            "description": "Список заказов",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "orders": [
                                {
                                    "id": "123e4567-e89b-12d3-a456-426614174000",
                                    "user_id": "123e4567-e89b-12d3-a456-426614174001",
                                    "items": [
                                        {
                                            "name": "Laptop",
                                            "amount": 2,
                                            "description": "High-performance laptop",
                                            "price": 1200.50
                                        }
                                    ],
                                    "status": "CREATED",
                                    "total_amount": 2401.00,
                                    "created_at": "2024-01-01T00:00:00",
                                    "updated_at": "2024-01-01T00:00:00"
                                }
                            ],
                            "total": 100,
                            "page": 1,
                            "size": 10,
                            "total_pages": 10
                        },
                        "error": None
                    }
                }
            }
        },
        401: {"description": "Не авторизован"}
    }
)
async def get_user_orders(
    page: int = Query(1, ge=1, description="Номер страницы"),
    size: int = Query(10, ge=1, le=100, description="Размер страницы"),
    sort_by: str = Query("created_at", description="Поле для сортировки (created_at, updated_at, total_amount)"),
    sort_order: str = Query("desc", description="Порядок сортировки (asc, desc)"),
    status: Optional[str] = Query(None, description="Фильтр по статусу (CREATED, IN_PROGRESS, COMPLETED, CANCELLED)"),
    current_user: Dict = Depends(get_required_user)
):
    """
    Получает список заказов текущего пользователя.
    
    - **page**: Номер страницы (начиная с 1)
    - **size**: Размер страницы (1-100)
    - **sort_by**: Поле для сортировки (created_at, updated_at, total_amount)
    - **sort_order**: Порядок сортировки (asc, desc)
    - **status**: Фильтр по статусу (опционально)
    
    Требуется авторизация (Bearer токен в заголовке Authorization).
    """
    query_params = {
        "page": page,
        "size": size,
        "sort_by": sort_by,
        "sort_order": sort_order
    }
    if status:
        query_params["status"] = status
    
    return await proxy.forward_request(
        service_url=settings.SERVICE_ORDERS_URL,
        path="v1/orders/my",
        method="GET",
        headers={"Authorization": f"Bearer {current_user['token']}"},
        query_params=query_params
    )


@router.put(
    "/{order_id}/status",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse,
    summary="Обновить статус заказа",
    description="Обновляет статус заказа с проверкой прав доступа",
    responses={
        200: {
            "description": "Статус заказа успешно обновлен",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "user_id": "123e4567-e89b-12d3-a456-426614174001",
                            "items": [
                                {
                                    "name": "Laptop",
                                    "amount": 2,
                                    "description": "High-performance laptop",
                                    "price": 1200.50
                                }
                            ],
                            "status": "IN_PROGRESS",
                            "total_amount": 2401.00,
                            "created_at": "2024-01-01T00:00:00",
                            "updated_at": "2024-01-01T00:10:00"
                        },
                        "error": None
                    }
                }
            }
        },
        401: {"description": "Не авторизован"},
        403: {"description": "Доступ запрещен (не ваш заказ)"},
        404: {"description": "Заказ не найден"},
        422: {"description": "Ошибка валидации (недопустимый статус или невозможно изменить статус)"}
    }
)
async def update_order_status(
    order_id: str,
    update_data: OrderUpdate,
    current_user: Dict = Depends(get_required_user)
):
    """
    Обновляет статус заказа.
    
    - **order_id**: UUID заказа
    - **status**: Новый статус (CREATED, IN_PROGRESS, COMPLETED, CANCELLED)
    
    Ограничения:
    - Нельзя изменить статус отмененного заказа
    - Нельзя изменить статус выполненного заказа
    
    Требуется авторизация (Bearer токен в заголовке Authorization).
    """
    return await proxy.forward_request(
        service_url=settings.SERVICE_ORDERS_URL,
        path=f"v1/orders/{order_id}/status",
        method="PUT",
        headers={"Authorization": f"Bearer {current_user['token']}"},
        json_data=update_data.model_dump(mode='json')
    )


@router.delete(
    "/{order_id}",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse,
    summary="Отменить заказ",
    description="Отменяет заказ (меняет статус на 'CANCELLED')",
    responses={
        200: {
            "description": "Заказ успешно отменен",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "user_id": "123e4567-e89b-12d3-a456-426614174001",
                            "items": [
                                {
                                    "name": "Laptop",
                                    "amount": 2,
                                    "description": "High-performance laptop",
                                    "price": 1200.50
                                }
                            ],
                            "status": "CANCELLED",
                            "total_amount": 2401.00,
                            "created_at": "2024-01-01T00:00:00",
                            "updated_at": "2024-01-01T00:10:00"
                        },
                        "error": None
                    }
                }
            }
        },
        401: {"description": "Не авторизован"},
        403: {"description": "Доступ запрещен (не ваш заказ)"},
        404: {"description": "Заказ не найден"},
        422: {"description": "Ошибка валидации (заказ уже отменен или нельзя отменить выполненный заказ)"}
    }
)
async def cancel_order(
    order_id: str,
    current_user: Dict = Depends(get_required_user)
):
    """
    Отменяет заказ.
    
    - **order_id**: UUID заказа
    
    Ограничения:
    - Нельзя отменить уже отмененный заказ
    - Нельзя отменить выполненный заказ
    
    Требуется авторизация (Bearer токен в заголовке Authorization).
    """
    return await proxy.forward_request(
        service_url=settings.SERVICE_ORDERS_URL,
        path=f"v1/orders/{order_id}",
        method="DELETE",
        headers={"Authorization": f"Bearer {current_user['token']}"}
    )
