import logging

logger = logging.getLogger(__name__)

_token_blocklist: set[str] = set()
_redis = None


async def get_conexion():
    global _redis
    if _redis is None:
        from app.core.config import config

        if not config.REDIS_HOST:
            return None
        import redis.asyncio as aioredis

        _redis = aioredis.Redis(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            db=config.REDIS_DB,
            decode_responses=True,
        )
        try:
            await _redis.ping()
            logger.info(
                "Redis conectado en %s:%s", config.REDIS_HOST, config.REDIS_PORT
            )
        except Exception as e:
            logger.warning("Redis no disponible (%s), usando blocklist en memoria", e)
            await _redis.aclose()
            _redis = None
    return _redis


async def esta_en_blocklist(jti: str) -> bool:
    r = await get_conexion()
    if r:
        return await r.sismember("token_blocklist", jti)
    return jti in _token_blocklist


async def agregar_a_blocklist(jti: str, ttl: int = 86400) -> None:
    r = await get_conexion()
    if r:
        await r.sadd("token_blocklist", jti)
        await r.expire("token_blocklist", ttl)
    else:
        _token_blocklist.add(jti)


async def cerrar():
    global _redis
    if _redis:
        await _redis.aclose()
        _redis = None
