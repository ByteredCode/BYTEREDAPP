import logging

logger = logging.getLogger(__name__)

# Blocklist hibrida: Redis como almacenamiento principal persistente (compartido entre workers)
# Fallback a set en memoria si Redis no esta disponible (ej. desarrollo local)
# Usamos un set (hashset) para busquedas O(1) en ambos casos
_token_blocklist: set[str] = set()
_redis = None


# Conexion lazy (bajo demanda): no bloquea el arranque de la app si Redis falla
# El singleton _redis se cachea tras el primer intento de conexion
async def get_conexion():
    global _redis
    if _redis is None:
        from app.core.config import config

        # Si no hay REDIS_HOST configurado, usamos directamente el fallback en memoria
        if not config.REDIS_HOST:
            return None
        # redis.asyncio en vez de redis sincrono para no bloquear el event loop de FastAPI
        import redis.asyncio as aioredis

        _redis = aioredis.Redis(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            db=config.REDIS_DB,
            # decode_responses=True devuelve strings en vez de bytes (mas comodo)
            decode_responses=True,
        )
        try:
            # ping() verifica que la conexion realmente funciona
            await _redis.ping()
            logger.info(
                "Redis conectado en %s:%s", config.REDIS_HOST, config.REDIS_PORT
            )
        except Exception as e:
            # Si Redis no responde, degradamos a memoria sin romper la app
            logger.warning("Redis no disponible (%s), usando blocklist en memoria", e)
            await _redis.aclose()
            _redis = None
    return _redis


# Consulta async: no bloquea el hilo mientras Redis responde
# sismember es O(1) en Redis (hash set), igual que el operador "in" en un set de Python
async def esta_en_blocklist(jti: str) -> bool:
    r = await get_conexion()
    if r:
        return await r.sismember("token_blocklist", jti)
    return jti in _token_blocklist


# TTL (time-to-live) en Redis: los tokens se limpian solos tras expirar
# 86400 segundos = 24h, suficiente para que el refresh token original expire
async def agregar_a_blocklist(jti: str, ttl: int = 86400) -> None:
    r = await get_conexion()
    if r:
        # sadd inserta en un set de Redis (sin duplicados)
        await r.sadd("token_blocklist", jti)
        # expire asegura que la clave completa se borre automaticamente
        await r.expire("token_blocklist", ttl)
    else:
        # Fallback en memoria: sin TTL se limpia al reiniciar la app
        _token_blocklist.add(jti)


# Cierre graceful: liberar la conexion Redis al apagar la aplicacion
async def cerrar():
    global _redis
    if _redis:
        await _redis.aclose()
        _redis = None
