from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

import crud
import schemas
from database import get_db

router = APIRouter(
    prefix="/checkout",
    tags=["checkout"],
)

@router.post("/", response_model=schemas.Order)
def create_order_endpoint(checkout_form: schemas.CheckoutForm, db: Session = Depends(get_db)):
    try:
        order = crud.create_order(db=db, checkout_form=checkout_form)
        return order
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        # Log the exception e
        raise HTTPException(status_code=500, detail="Internal Server Error")


