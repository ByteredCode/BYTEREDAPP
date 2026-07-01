import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import config
from app.core.security import hash_contrasena
from app.models.empresa import Empresa
from app.models.usuario import Usuario

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("auto_seed")

ADMIN_CORREO = "antonio@bytered.es"
ADMIN_CONTRASENA = "admin1234A"
ADMIN_NOMBRE = "Antonio"


async def auto_seed():
    database_url = config.database_url
    engine = create_async_engine(database_url, echo=False)
    Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with Session() as session:
        total_empresas = await session.scalar(select(func.count(Empresa.codigo_empresa)))
        if total_empresas and total_empresas > 0:
            admin = await session.scalar(
                select(Usuario).where(Usuario.rol == "admin_total").limit(1)
            )
            if admin:
                admin.correo = ADMIN_CORREO
                admin.contrasena = hash_contrasena(ADMIN_CONTRASENA)
                admin.nombre = ADMIN_NOMBRE
                await session.commit()
                logger.info("Admin actualizado: %s / %s", ADMIN_CORREO, ADMIN_CONTRASENA)
                await engine.dispose()
                return
            empresa = await session.scalar(select(Empresa).limit(1))
            if not empresa:
                logger.info("No hay empresas en la BD")
                await engine.dispose()
                return
            admin = Usuario(
                correo=ADMIN_CORREO,
                contrasena=hash_contrasena(ADMIN_CONTRASENA),
                nombre=ADMIN_NOMBRE,
                rol="admin_total",
                codigo_empresa=empresa.codigo_empresa,
            )
            session.add(admin)
            await session.commit()
            logger.info("Admin creado: %s / %s", ADMIN_CORREO, ADMIN_CONTRASENA)
        else:
            empresa = Empresa(nombre="ByteRed Solutions SL")
            session.add(empresa)
            await session.flush()
            logger.info("Empresa creada: %s (id %s)", empresa.nombre, empresa.codigo_empresa)
            admin = Usuario(
                correo=ADMIN_CORREO,
                contrasena=hash_contrasena(ADMIN_CONTRASENA),
                nombre=ADMIN_NOMBRE,
                rol="admin_empresa",
                codigo_empresa=empresa.codigo_empresa,
            )
            session.add(admin)
            await session.commit()
            logger.info("Admin creado: %s / %s", ADMIN_CORREO, ADMIN_CONTRASENA)

        logger.info("Seed automático completado")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(auto_seed())
