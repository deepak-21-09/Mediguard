"""Redis client — optional. If REDIS_URL is empty, all operations are no-ops."""
from core.config import settings

redis_client = None


async def get_redis():
    return redis_client


async def init_redis():
    global redis_client
    if not settings.REDIS_URL:
        return
    try:
        import redis.asyncio as aioredis
        redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    except Exception as e:
        print(f"[Redis] Could not connect: {e}. Continuing without Redis.")


async def close_redis():
    global redis_client
    if redis_client:
        await redis_client.close()
