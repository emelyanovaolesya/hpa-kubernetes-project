from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional, Dict
from app.database import get_db
from app.schemas.order import OrderCreate, OrderUpdate, OrderResponse, OrderListResponse, OrderItem
from app.schemas.response import success_response
from app.services.order_service import OrderService
from app.core.dependencies import get_current_user

router = APIRouter()


@router.post(
    "/",
    response_model=None,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый заказ",
    description="Создает новый заказ для текущего авторизованного пользователя"
)
@router.post(
    "/create",
    response_model=None,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый заказ",
    description="Создает новый заказ для текущего авторизованного пользователя"
)
def create_order(
    order_data: OrderCreate,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Создает новый заказ.
    """
    order = OrderService.create_order(db, order_data, current_user["user_id"])
    
    order_response = OrderResponse.model_validate(order)
    order_dict = order_response.model_dump()
    order_dict["items"] = [OrderItem(**item) for item in order_dict["items"]]
    
    return success_response(order_response.model_dump())


@router.get(
    "/{order_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Получить заказ по ID",
    description="Возвращает информацию о заказе по его идентификатору"
)
def get_order(
    order_id: str,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получает заказ по ID с проверкой прав доступа.
    """
    order = OrderService.get_order_by_id(db, order_id, current_user["user_id"])
    order_response = OrderResponse.model_validate(order)
    return success_response(order_response.model_dump())


@router.get(
    "/",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Получить список заказов текущего пользователя",
    description="Возвращает список заказов с пагинацией, сортировкой и фильтрацией"
)
@router.get(
    "/my",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Получить список заказов текущего пользователя",
    description="Возвращает список заказов с пагинацией, сортировкой и фильтрацией"
)
def get_user_orders(
    page: int = Query(1, ge=1, description="Номер страницы"),
    size: int = Query(10, ge=1, le=100, description="Размер страницы"),
    sort_by: str = Query("created_at", description="Поле для сортировки (created_at, updated_at, total_amount)"),
    sort_order: str = Query("desc", description="Порядок сортировки (asc, desc)"),
    status: Optional[str] = Query(None, description="Фильтр по статусу"),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получает список заказов текущего пользователя.
    """
    orders, total = OrderService.get_user_orders(
        db,
        user_id=current_user["user_id"],
        page=page,
        size=size,
        sort_by=sort_by,
        sort_order=sort_order,
        status_filter=status
    )
    
    total_pages = OrderService.calculate_total_pages(total, size)
    
    order_list_response = OrderListResponse(
        orders=[OrderResponse.model_validate(order) for order in orders],
        total=total,
        page=page,
        size=size,
        total_pages=total_pages
    )
    
    return success_response(order_list_response.model_dump())


@router.put(
    "/{order_id}/status",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Обновить статус заказа",
    description="Обновляет статус заказа с проверкой прав доступа"
)
def update_order_status(
    order_id: str,
    update_data: OrderUpdate,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Обновляет статус заказа.
    """
    order = OrderService.update_order_status(
        db,
        order_id,
        current_user["user_id"],
        update_data
    )
    order_response = OrderResponse.model_validate(order)
    return success_response(order_response.model_dump())


@router.delete(
    "/{order_id}",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Отменить заказ",
    description="Отменяет заказ (меняет статус на 'CANCELLED')"
)
def cancel_order(
    order_id: str,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Отменяет заказ.
    """
    order = OrderService.cancel_order(db, order_id, current_user["user_id"])
    order_response = OrderResponse.model_validate(order)
    return success_response(order_response.model_dump())
