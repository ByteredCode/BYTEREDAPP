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


async def auto_seed():
    database_url = config.database_url
    engine = create_async_engine(database_url, echo=False)
    Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with Session() as session:
        total_empresas = await session.scalar(select(func.count(Empresa.codigo_empresa)))
        if total_empresas and total_empresas > 0:
            logger.info("Ya existen empresas en la BD — seed automático omitido")
            await engine.dispose()
            return

        empresa = Empresa(nombre="ByteRed Solutions SL")
        session.add(empresa)
        await session.flush()
        logger.info("Empresa creada: %s (id %s)", empresa.nombre, empresa.codigo_empresa)

        admin = Usuario(
            correo="admin@byteredapp.com",
            contrasena=hash_contrasena("Admin1234"),
            nombre="Admin ByteRed",
            rol="admin_empresa",
            codigo_empresa=empresa.codigo_empresa,
        )
        session.add(admin)
        await session.flush()
        logger.info("Admin creado: admin@byteredapp.com / Admin1234")

        await session.commit()
        logger.info("Seed automático completado")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(auto_seed())
