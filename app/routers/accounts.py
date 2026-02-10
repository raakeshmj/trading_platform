from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.user import AccountRead
from app.services import account as account_service

router = APIRouter(prefix="/accounts", tags=["accounts"])

@router.get("/me", response_model=AccountRead)
async def get_my_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    account = await account_service.get_account_by_user_id(db, current_user.id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account
