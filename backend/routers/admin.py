from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session
from typing import List, Optional

import crud
import schemas
from database import get_db
from enum import Enum

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)


class AdminVariantStatusFilter(str, Enum):
    ACTIVE = "active"
    SOLD_OUT = "sold_out"
    INACTIVE = "inactive"
    DISCONTINUED = "discontinued"


@router.get("/products", response_model=schemas.AdminProductList)
def read_all_products_for_admin(
    skip: int = 0,
    limit: int = 100,
    category_slug: Optional[str] = Query(None),
    brand_slugs: Optional[List[str]] = Query(None, alias="brands"),
    size_values: Optional[List[str]] = Query(None, alias="sizes"),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    sort_by: Optional[str] = Query(
        None, description="Sort by: 'price_asc', 'price_desc', 'name_asc', 'name_desc'"
    ),
    max_stock: Optional[int] = Query(
        None,
        description="Filter for products with total stock less than or equal to this value",
    ),
    status: Optional[AdminVariantStatusFilter] = Query(
        None, description="Filter by variant status"
    ),
    db: Session = Depends(get_db),
):
    """
    Retrieve products for the admin panel with optional filtering and pagination.
    Returns all products, including out-of-stock items and status.
    """
    products, total_count = crud.get_products_for_admin(
        db,
        skip=skip,
        limit=limit,
        category_slug=category_slug,
        brand_slugs=brand_slugs,
        size_values=size_values,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by,
        max_stock=max_stock,
        status=status,
    )
    return {"products": products, "total_count": total_count}


@router.patch("/{order_id}/status", response_model=schemas.Order)
def update_order_status_endpoint(
    status_update: schemas.OrderStatusUpdate,
    order_id: int = Path(..., description="ID заказа для обновления статуса"),
    db: Session = Depends(get_db),
):
    """
    Обновляет статус заказа.

    - **order_id**: ID заказа
    - **status**: Новый статус заказа

    Доступные статусы:
    - pending: В ожидании
    - confirmed: Подтвержден
    - processing: В обработке
    - shipped: Отправлен
    - delivered: Доставлен
    - cancelled: Отменен
    - refunded: Возвращен

    При отмене заказа (cancelled) товары автоматически возвращаются на склад.
    """
    try:
        updated_order = crud.update_order_status(
            db=db, order_id=order_id, status=status_update.status
        )

        if not updated_order:
            raise HTTPException(
                status_code=404, detail=f"Заказ с ID {order_id} не найден"
            )

        return updated_order

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Логируем ошибку
        print(f"Ошибка при обновлении статуса заказа {order_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Внутренняя ошибка сервера при обновлении статуса заказа",
        )


@router.get("/{order_id}", response_model=schemas.AdminOrder)
def get_order_endpoint(order_id: int, db: Session = Depends(get_db)):
    """
    Получает заказ по ID.

    Args:
        order_id: ID заказа
        db: Сессия базы данных

    Returns:
        Order: Данные заказа

    Raises:
        HTTPException: 404 если заказ не найден
    """
    order = crud.get_order_by_id(db=db, order_id=order_id)

    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")

    return order

