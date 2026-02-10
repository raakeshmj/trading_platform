from pydantic import BaseModel, Field, condecimal
from typing import Optional
from datetime import datetime

class InstrumentCreate(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=10)
    name: str
    current_price: condecimal(max_digits=18, decimal_places=4) = Field(..., gt=0)

class InstrumentRead(InstrumentCreate):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
