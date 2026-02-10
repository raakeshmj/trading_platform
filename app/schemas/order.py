from pydantic import BaseModel, Field, condecimal
from typing import Optional
from datetime import datetime
from app.models.order import OrderSide, OrderType, OrderStatus

class OrderCreate(BaseModel):
    instrument_symbol: str
    side: OrderSide
    type: OrderType
    quantity: int = Field(..., gt=0)
    price: Optional[condecimal(max_digits=18, decimal_places=4)] = None

class OrderRead(BaseModel):
    id: int
    instrument_id: int
    side: OrderSide
    type: OrderType
    status: OrderStatus
    price: Optional[condecimal(max_digits=18, decimal_places=4)]
    quantity: int
    filled_quantity: int
    created_at: datetime
    
    class Config:
        from_attributes = True
