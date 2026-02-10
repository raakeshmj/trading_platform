from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import Account

async def get_account_by_user_id(db: AsyncSession, user_id: int):
    result = await db.execute(select(Account).where(Account.user_id == user_id))
    return result.scalars().first()
