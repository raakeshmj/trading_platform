from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.instrument import InstrumentCreate, InstrumentRead
from app.services import instrument as instrument_service

# Note: In a real app, Create/Update might be restricted to admins.
# For this simulation, we'll allow authenticated users to create instruments for testing.

router = APIRouter(prefix="/instruments", tags=["instruments"])

@router.post("/", response_model=InstrumentRead, status_code=status.HTTP_201_CREATED)
async def create_instrument(
    instrument_in: InstrumentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    existing = await instrument_service.get_instrument_by_symbol(db, instrument_in.symbol)
    if existing:
        raise HTTPException(status_code=400, detail="Instrument with this symbol already exists")
    
    return await instrument_service.create_instrument(db, instrument_in)

@router.get("/", response_model=List[InstrumentRead])
async def list_instruments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await instrument_service.get_all_instruments(db)

@router.get("/{symbol}", response_model=InstrumentRead)
async def get_instrument(
    symbol: str, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    instrument = await instrument_service.get_instrument_by_symbol(db, symbol)
    if not instrument:
        raise HTTPException(status_code=404, detail="Instrument not found")
    return instrument
