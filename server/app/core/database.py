# SQLAlchemy asincrono con aiomysql: necesario para FastAPI (asincrono por naturaleza)
# Si usasemos pymysql sincrono, cada consulta bloquearia el event loop
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import config

# create_async_engine usa aiomysql internamente (por el prefijo mysql+aiomysql)
# echo=False evita loggear cada query en produccion (rendimiento y seguridad)
engine = create_async_engine(config.database_url, echo=False)
# expire_on_commit=False: por defecto SQLAlchemy expira objetos tras commit
# Lo desactivamos para poder seguir accediendo a atributos despues del commit
async_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    # AsyncAttrs permite lazy loading en modo async (acceder a relaciones sin await explicito)
    # DeclarativeBase mapea clases Python a tablas SQL (ORM clasico de SQLAlchemy)
    pass


# Generator de FastAPI: se crea una sesion por peticion HTTP
# FastAPI maneja el ciclo de vida: abre antes de la ruta, cierra despues
async def get_db():
    async with async_session() as session:
        yield session
