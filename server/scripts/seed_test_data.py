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
from app.models.ticket import Ticket

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("seed_test_data")

EMPRESAS = [
    {"nombre": "ByteRed Solutions SL", "web": "https://byteredapp.com"},
    {"nombre": "TechCorp España", "web": "https://techcorp.es"},
    {"nombre": "InnovaSoft", "web": "https://innovasoft.com"},
]

USUARIOS = [
    {"correo": "admin@bytered.es", "contrasena": "Admin1234", "nombre": "Antonio (Admin Total)", "rol": "admin_total", "empresa": 0},
    {"correo": "maria@techcorp.es", "contrasena": "Maria1234", "nombre": "María García", "rol": "admin_empresa", "empresa": 1},
    {"correo": "carlos@techcorp.es", "contrasena": "Carlos1234", "nombre": "Carlos López", "rol": "usuario", "empresa": 1},
    {"correo": "laura@innova.es", "contrasena": "Laura1234", "nombre": "Laura Martínez", "rol": "admin_empresa", "empresa": 2},
    {"correo": "pedro@innova.es", "contrasena": "Pedro1234", "nombre": "Pedro Sánchez", "rol": "usuario", "empresa": 2},
]

TICKETS = [
    {"asunto": "Problema con el login", "mensaje": "No puedo iniciar sesión desde ayer", "nivel_importancia": "Alta", "empresa": 1, "contacto": "carlos@techcorp.es"},
    {"asunto": "Error al generar PDF", "mensaje": "La exportación a PDF no funciona en el módulo de documentos", "nivel_importancia": "Media", "empresa": 1, "contacto": "maria@techcorp.es"},
    {"asunto": "Mejora en el tablero Kanban", "mensaje": "Sería útil poder filtrar tareas por prioridad", "nivel_importancia": "Baja", "empresa": 2, "contacto": "laura@innova.es"},
    {"asunto": "Error 500 al guardar", "mensaje": "Al guardar un ticket nuevo da error interno del servidor", "nivel_importancia": "Critica", "empresa": 2, "contacto": "pedro@innova.es"},
    {"asunto": "Solicitud de nueva funcionalidad", "mensaje": "Necesitamos un módulo de facturación", "nivel_importancia": "Media", "empresa": 0, "contacto": "admin@bytered.es"},
]


async def seed_test_data():
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

        logger.info("Creando usuarios de prueba...")
        for u_data in USUARIOS:
            existe = await session.scalar(select(Usuario).where(Usuario.correo == u_data["correo"]).limit(1))
            if existe:
                logger.info("  Usuario ya existe: %s (%s)", existe.nombre, existe.correo)
                continue
            usuario = Usuario(
                correo=u_data["correo"],
                contrasena=hash_contrasena(u_data["contrasena"]),
                nombre=u_data["nombre"],
                rol=u_data["rol"],
                codigo_empresa=empresas_ids[u_data["empresa"]],
            )
            session.add(usuario)
            await session.flush()
            logger.info("  Usuario creado: %s (%s) - %s", usuario.nombre, usuario.correo, usuario.rol)

        logger.info("Creando tickets de prueba...")
        for t_data in TICKETS:
            existe = await session.scalar(
                select(Ticket).where(Ticket.asunto == t_data["asunto"]).limit(1)
            )
            if existe:
                logger.info("  Ticket ya existe: %s", existe.asunto)
                continue
            ticket = Ticket(
                asunto=t_data["asunto"],
                mensaje=t_data["mensaje"],
                nivel_importancia=t_data["nivel_importancia"],
                codigo_empresa=empresas_ids[t_data["empresa"]],
                correo_contacto=t_data["contacto"],
            )
            session.add(ticket)
            logger.info("  Ticket creado: %s", ticket.asunto)

        await session.commit()
        logger.info("Seed de datos de prueba completado")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_test_data())
