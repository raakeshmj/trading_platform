from pydantic import BaseModel, Field, condecimal
from typing import Optional
from datetime import datetime

class AccountRead(BaseModel):
    id: int
    user_id: int
    cash_balance: condecimal(max_digits=18, decimal_places=4)
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
