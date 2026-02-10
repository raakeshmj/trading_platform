from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.order import OrderCreate, OrderRead
from app.services import order as order_service

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
async def place_order(
    order_in: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        return await order_service.create_order(db, order_in, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    # Custom exceptions handled by middleware or global handler if registered, 
    # but specific handling here is also fine.

@router.get("/", response_model=List[OrderRead])
async def list_orders(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await order_service.get_user_orders(db, current_user.id)
