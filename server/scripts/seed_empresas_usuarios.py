import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import config
from app.core.security import hash_contrasena
from app.models.empresa import Empresa
from app.models.empresa_servicio import EmpresaServicio
from app.models.usuario import Usuario

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("seed_empresas_usuarios")

EMPRESAS = [
    {"nombre": "ByteRed Solutions SL", "web": "https://byteredapp.com"},
    {"nombre": "TechCorp España", "web": "https://techcorp.es"},
    {"nombre": "InnovaSoft", "web": "https://innovasoft.com"},
]

USUARIOS_POR_EMPRESA = [
    {"correo": "ana@bytered.es", "contrasena": "Ana12345", "nombre": "Ana Belén Ruiz", "rol": "admin_empresa"},
    {"correo": "jorge@bytered.es", "contrasena": "Jorge1234", "nombre": "Jorge Moreno", "rol": "usuario"},
    {"correo": "lucia@bytered.es", "contrasena": "Lucia1234", "nombre": "Lucía Herrera", "rol": "usuario"},
    {"correo": "david@bytered.es", "contrasena": "David1234", "nombre": "David Gil", "rol": "usuario"},
    {"correo": "elena@bytered.es", "contrasena": "Elena1234", "nombre": "Elena Torres", "rol": "usuario"},
    {"correo": "raul@techcorp.es", "contrasena": "Raul12345", "nombre": "Raúl Domínguez", "rol": "admin_empresa"},
    {"correo": "sonia@techcorp.es", "contrasena": "Sonia1234", "nombre": "Sonia Ramos", "rol": "usuario"},
    {"correo": "pablo@techcorp.es", "contrasena": "Pablo1234", "nombre": "Pablo Vargas", "rol": "usuario"},
    {"correo": "nuria@techcorp.es", "contrasena": "Nuria1234", "nombre": "Nuria Castro", "rol": "usuario"},
    {"correo": "alberto@techcorp.es", "contrasena": "Alberto12", "nombre": "Alberto Medina", "rol": "usuario"},
    {"correo": "marta@innova.es", "contrasena": "Marta1234", "nombre": "Marta Iglesias", "rol": "admin_empresa"},
    {"correo": "sergio@innova.es", "contrasena": "Sergio123", "nombre": "Sergio Rivas", "rol": "usuario"},
    {"correo": "cris@innova.es", "contrasena": "Cris12345", "nombre": "Cristina Navarro", "rol": "usuario"},
    {"correo": "ivan@innova.es", "contrasena": "Ivan12345", "nombre": "Iván Delgado", "rol": "usuario"},
    {"correo": "patri@innova.es", "contrasena": "Patri1234", "nombre": "Patricia Flores", "rol": "usuario"},
]

async def seed():
    database_url = config.database_url
    engine = create_async_engine(database_url, echo=False)
    Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with Session() as session:
        logger.info("Creando empresas de prueba...")
        empresas_ids = []
        for e_data in EMPRESAS:
            existe = await session.scalar(select(Empresa).where(Empresa.nombre == e_data["nombre"]).limit(1))
            if existe:
                logger.info("  Empresa ya existe: %s (id %s)", existe.nombre, existe.codigo_empresa)
                empresas_ids.append(existe.codigo_empresa)
                continue
            empresa = Empresa(nombre=e_data["nombre"], web=e_data["web"])
            session.add(empresa)
            await session.flush()
            for servicio in ["scrum", "tickets", "documentacion", "fichaje", "redireccion"]:
                session.add(EmpresaServicio(codigo_empresa=empresa.codigo_empresa, servicio=servicio, activo=True))
            empresas_ids.append(empresa.codigo_empresa)
            logger.info("  Empresa creada: %s (id %s)", empresa.nombre, empresa.codigo_empresa)

        if not empresas_ids:
            logger.warning("No hay empresas disponibles. Abortando.")
            return

        logger.info("Creando 5 usuarios por empresa (%s empresas)...", len(empresas_ids))
        idx = 0
        for i, cod_emp in enumerate(empresas_ids):
            for _ in range(5):
                u_data = USUARIOS_POR_EMPRESA[idx]
                existe = await session.scalar(select(Usuario).where(Usuario.correo == u_data["correo"]).limit(1))
                if existe:
                    logger.info("  Usuario ya existe: %s (%s)", existe.nombre, existe.correo)
                else:
                    usuario = Usuario(
                        correo=u_data["correo"],
                        contrasena=hash_contrasena(u_data["contrasena"]),
                        nombre=u_data["nombre"],
                        rol=u_data["rol"],
                        codigo_empresa=cod_emp,
                    )
                    session.add(usuario)
                    await session.flush()
                    logger.info("  Usuario creado: %s (%s) - %s", usuario.nombre, usuario.correo, usuario.rol)
                idx += 1

        await session.commit()
        logger.info("Seed completado: %s empresas, %s usuarios", len(empresas_ids), idx)

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(seed())
