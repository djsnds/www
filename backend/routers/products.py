from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

import crud
import schemas
from database import get_db

router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@router.get("/", response_model=schemas.ProductList)
def read_products(
    skip: int = 0,
    limit: int = 12,
    category_slug: Optional[str] = Query(None),
    brand_slugs: Optional[List[str]] = Query(None, alias="brands"),
    size_values: Optional[List[str]] = Query(None, alias="sizes"),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    sort_by: Optional[str] = Query(
        None, description="Sort by: 'price_asc', 'price_desc', 'name_asc', 'name_desc'"
    ),
    db: Session = Depends(get_db),
):
    products, total_count = crud.get_products(
        db,
        skip=skip,
        limit=limit,
        category_slug=category_slug,
        brand_slugs=brand_slugs,
        size_values=size_values,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by,
    )

    return {"products": products, "total_count": total_count}


@router.get("/filters", response_model=schemas.FilterOptions)
def get_filters(category_slug: str, db: Session = Depends(get_db)):
    """
    Retrieve available brands and sizes for a given category.
    """
    return crud.get_filters_for_category(db, category_slug=category_slug)


@router.get("/{product_id}", response_model=schemas.ProductDetail)
def read_product(product_id: int, db: Session = Depends(get_db)):
    db_product = crud.get_product_by_id(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product
