import asyncio
import random
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import SessionLocal
from app.services import instrument as instrument_service
from app.services.event import publish_trade # Reusing trade channel for ticker? Or new channel?
# reusing trade channel might confuse. Let's send a specific "ticker" event.
from app.redis import get_redis
import json

async def run_market_feed():
    """
    Simulates external market moves by broadcasting 'ticker' updates.
    Does NOT match orders or create trades. Just updates the 'display' price
    and maybe places random orders if we wanted a full bot.
    For simplicity, this just broadcasts 'ticker' events to make the UI alive.
    """
    redis = await get_redis()
    while True:
        try:
            async with SessionLocal() as db:
                instruments = await instrument_service.get_all_instruments(db)
                if not instruments:
                    await asyncio.sleep(5)
                    continue
                
                # Pick random instrument
                instrument = random.choice(instruments)
                
                # Random move: -0.5% to +0.5%
                change_pct = random.uniform(-0.005, 0.005)
                new_price = float(instrument.current_price) * (1 + change_pct)
                new_price = round(new_price, 2)
                
                # Update DB (optional, maybe too much write load? let's do it)
                instrument.current_price = new_price
                db.add(instrument)
                await db.commit()
                
                # Publish Ticker
                event = {
                    "symbol": instrument.symbol,
                    "price": new_price,
                    "timestamp": asyncio.get_event_loop().time()
                }
                
                # We publish to the same 'trades' channel or a new 'ticker' channel?
                # User requirement: "Publish trade and order updates... Expose WebSocket... live order book"
                # "Allow price updates (mock market feed)"
                # I'll publish to "trades:{symbol}" disguised as a trade or separate?
                # Let's use a "ticker:{symbol}" channel if we had one.
                # For now, I'll piggyback on 'trades' but mark it `is_mock=True` or just let it interpret as last price.
                # Or better: Just create orders!
                pass 
                
        except Exception as e:
            print(f"Market feed error: {e}")
        
        await asyncio.sleep(1) # Frequency

# Re-thinking: A background task that just creates NOISE is not as useful as one that Provides Liquidity.
# But providing liquidity requires a User with Funds.
# I will skip the complex Market Maker Bot for now and just implement the basic app structure.
# I can rely on the User to place orders to see it work.
# The "Mock Market Feed" requirement: "Maintain live market price simulation".
# I'll stick to the simple updates.

async def market_simulation_task():
    """
    Simulates market activity by publishing fake trade events.
    This makes the frontend/WebSocket feel alive even without user orders.
    """
    redis = await get_redis()
    print("Starting market simulation feed...")
    
    while True:
        try:
            # Create a new session for each iteration to get fresh data
            async with SessionLocal() as db:
                instruments = await instrument_service.get_all_instruments(db)
                
            if not instruments:
                await asyncio.sleep(5)
                continue
            
            # Pick a random instrument
            instrument = random.choice(instruments)
            
            # Fluctuate price around current price
            # We use the stored price as the anchor
            current_price = float(instrument.current_price)
            change_pct = random.uniform(-0.002, 0.002) # +/- 0.2%
            trade_price = round(current_price * (1 + change_pct), 2)
            
            # Fake trade size
            trade_qty = random.randint(1, 100)
            
            # Publish event
            # We publish to the 'trades' channel so subscribers see it.
            # We add a flag 'is_simulation': True so clients can distinguish if they want.
            event = {
                "symbol": instrument.symbol,
                "price": trade_price,
                "quantity": trade_qty,
                "timestamp": asyncio.get_event_loop().time(),
                "is_simulation": True
            }
            channel = f"trades:{instrument.symbol}"
            await redis.publish(channel, json.dumps(event))
            
            # Optional: We could update the DB price too, but that requires a write.
            # Let's interact with the DB properly? No, let's keep it simple read-only
            # effectively just a "ticker" feed.
            
        except Exception as e:
            print(f"Market simulation error: {e}")
            
        await asyncio.sleep(random.uniform(0.5, 2.0)) # Random interval
