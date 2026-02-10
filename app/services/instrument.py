from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.instrument import Instrument
from app.schemas.instrument import InstrumentCreate

async def create_instrument(db: AsyncSession, instrument_in: InstrumentCreate):
    db_instrument = Instrument(
        symbol=instrument_in.symbol.upper(),
        name=instrument_in.name,
        current_price=instrument_in.current_price
    )
    db.add(db_instrument)
    await db.commit()
    await db.refresh(db_instrument)
    return db_instrument

async def get_all_instruments(db: AsyncSession):
    result = await db.execute(select(Instrument).where(Instrument.is_active == True))
    return result.scalars().all()

async def get_instrument_by_symbol(db: AsyncSession, symbol: str):
    result = await db.execute(select(Instrument).where(Instrument.symbol == symbol.upper()))
    return result.scalars().first()
