from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import config

# Motor asincrono: cada operacion de BD no bloquea el event loop
engine = create_async_engine(config.database_url, echo=False)
# expire_on_commit=False permite seguir usando objetos tras hacer commit
async_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    # AsyncAttrs permite lazy loading en modo async
    # DeclarativeBase mapea clases Python a tablas SQL
    pass


# Dependencia de FastAPI: una sesion por peticion, se cierra automaticamente
async def get_db():
    async with async_session() as session:
        yield session
