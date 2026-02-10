import json
from app.redis import get_redis

async def publish_trade(trade_data: dict, symbol: str):
    redis = await get_redis()
    channel = f"trades:{symbol}"
    await redis.publish(channel, json.dumps(trade_data, default=str))

async def publish_orderbook_update(symbol: str, depth: dict):
    redis = await get_redis()
    channel = f"orderbook:{symbol}"
    await redis.publish(channel, json.dumps(depth, default=str))
