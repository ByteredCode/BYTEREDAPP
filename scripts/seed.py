import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "server"))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import config
from app.core.security import hash_contrasena
from app.models.empresa import Empresa
from app.models.usuario import Usuario
from app.models.sprint import Sprint
from app.models.tarea import Tarea
from app.models.ticket import Ticket
from app.models.documento import Documento

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("seed")

DATOS = {
    "empresa": {"nombre": "ByteRed Solutions SL"},
    "admin": {
        "correo": "admin@byteredapp.com",
        "contrasena": "Admin1234",
        "nombre": "Admin ByteRed",
        "rol": "admin_empresa",
    },
    "usuarios": [
        {"correo": "ana@byteredapp.com", "contrasena": "Test1234", "nombre": "Ana García"},
        {"correo": "carlos@byteredapp.com", "contrasena": "Test1234", "nombre": "Carlos López"},
    ],
    "sprints": [
        {"nombre": "Sprint 1", "objetivo": "MVP", "estado": "Completado"},
        {"nombre": "Sprint 2", "objetivo": "Mejoras UX", "estado": "Activo"},
    ],
    "tareas": [
        {"titulo": "Configurar servidor", "prioridad": "Alta", "columna": "Done"},
        {"titulo": "Diseñar login", "prioridad": "Media", "columna": "En revision"},
        {"titulo": "Implementar API", "prioridad": "Alta", "columna": "Haciendose"},
        {"titulo": "Tests unitarios", "prioridad": "Media", "columna": "Todo"},
    ],
    "tickets": [
        {"nombre_contacto": "Cliente A", "correo_contacto": "cliente@test.com", "asunto": "Error al iniciar sesión", "mensaje": "No puedo acceder con mis credenciales.", "nivel_importancia": "Alta"},
        {"nombre_contacto": "Cliente B", "asunto": "Sugerencia", "mensaje": "Podrían añadir modo oscuro.", "nivel_importancia": "Baja"},
    ],
}


async def seed():
    database_url = config.database_url.replace("mysql+aiomysql://", "mysql+aiomysql://")
    engine = create_async_engine(database_url, echo=False)
    Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with Session() as session:
        empresa = Empresa(**DATOS["empresa"])
        session.add(empresa)
        await session.flush()
        logger.info("Empresa creada: %s (id %s)", empresa.nombre, empresa.codigo_empresa)

        admin_data = DATOS["admin"].copy()
        admin_data["contrasena"] = hash_contrasena(admin_data["contrasena"])
        admin_data["codigo_empresa"] = empresa.codigo_empresa
        admin = Usuario(**admin_data)
        session.add(admin)

        usuarios = []
        for u_data in DATOS["usuarios"]:
            data = u_data.copy()
            data["contrasena"] = hash_contrasena(data["contrasena"])
            data["codigo_empresa"] = empresa.codigo_empresa
            u = Usuario(**data)
            session.add(u)
            usuarios.append(u)

        await session.flush()
        logger.info("Usuarios creados: %d", len(usuarios) + 1)

        sprints = []
        for s_data in DATOS["sprints"]:
            s = Sprint(codigo_empresa=empresa.codigo_empresa, **s_data)
            session.add(s)
            sprints.append(s)
        await session.flush()
        logger.info("Sprints creados: %d", len(sprints))

        for i, t_data in enumerate(DATOS["tareas"]):
            tarea = Tarea(
                codigo_empresa=empresa.codigo_empresa,
                codigo_sprint=sprints[0].codigo_sprint,
                asignacion=usuarios[i % len(usuarios)].codigo_usuario,
                **t_data,
            )
            session.add(tarea)
        logger.info("Tareas creadas: %d", len(DATOS["tareas"]))

        for tk_data in DATOS["tickets"]:
            ticket = Ticket(
                codigo_empresa=empresa.codigo_empresa,
                estado="Pendiente",
                **tk_data,
            )
            session.add(ticket)
        logger.info("Tickets creados: %d", len(DATOS["tickets"]))

        await session.commit()
        logger.info("Seed completado. Empresa: %s | Admin: admin@byteredapp.com / Admin1234", empresa.codigo_empresa)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
