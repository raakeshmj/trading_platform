import redis.asyncio as redis
from app.config import settings

# Global Redis pool
redis_pool = None

async def init_redis():
    global redis_pool
    redis_pool = redis.ConnectionPool.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True
    )

async def close_redis():
    global redis_pool
    if redis_pool:
        await redis_pool.disconnect()

async def get_redis() -> redis.Redis:
    if redis_pool is None:
        await init_redis()
    return redis.Redis(connection_pool=redis_pool)
