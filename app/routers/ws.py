import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.redis import get_redis
from app.services.matching_engine import matching_engine

router = APIRouter(tags=["websocket"])

@router.websocket("/ws/{symbol}")
async def websocket_endpoint(websocket: WebSocket, symbol: str):
    await websocket.accept()
    redis = await get_redis()
    pubsub = redis.pubsub()
    
    # Subscribe to channels
    await pubsub.subscribe(f"trades:{symbol}", f"orderbook:{symbol}")
    
    # Send initial snapshot
    engine = matching_engine
    book = await engine.get_orderbook(symbol)
    snapshot = {
        "type": "snapshot",
        "data": book.depth()
    }
    await websocket.send_json(snapshot)
    
    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True)
            if message:
                channel = message["channel"]
                data = json.loads(message["data"])
                
                msg_type = "trade" if "trades" in channel else "orderbook"
                
                await websocket.send_json({
                    "type": msg_type,
                    "data": data
                })
            
            await asyncio.sleep(0.01) # Prevent tight loop CPU usage
    except WebSocketDisconnect:
        await pubsub.unsubscribe()
