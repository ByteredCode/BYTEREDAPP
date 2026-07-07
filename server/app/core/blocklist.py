import logging

logger = logging.getLogger(__name__)

# Blocklist hibrida: Redis como almacenamiento principal persistente (compartido entre workers)
# Fallback a set en memoria si Redis no esta disponible (ej. desarrollo local)
# Usamos claves individuales por JTI con TTL propio para evitar que se borren en lote
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
# Claves individuales por JTI con verificacion O(1)
async def esta_en_blocklist(jti: str) -> bool:
    r = await get_conexion()
    if r:
        return await r.exists(f"bl:{jti}")
    return jti in _token_blocklist


# TTL individual por JTI: access token = 30min, refresh token = 7 dias
# Se usa el TTL del token mas largo (refresh = 7d = 604800s) como maximo
# Cada JTI se limpia automaticamente cuando su token expira
async def agregar_a_blocklist(jti: str, ttl: int = 604800) -> None:
    r = await get_conexion()
    if r:
        # Clave individual por JTI con TTL propio — no se borra en lote
        await r.set(f"bl:{jti}", "1", ex=ttl)
    else:
        # Fallback en memoria: sin TTL se limpia al reiniciar la app
        _token_blocklist.add(jti)


# Cierre graceful: liberar la conexion Redis al apagar la aplicacion
async def cerrar():
    global _redis
    if _redis:
        await _redis.aclose()
        _redis = None
