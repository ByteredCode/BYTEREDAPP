import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import config
from app.models.tarea import Tarea


TAREAS_15 = [
    # Todo (4)
    {"titulo": "Disenar mockups landing page", "descripcion": "Prototipos en Figma", "prioridad": "Alta", "columna": "Todo"},
    {"titulo": "Configurar CI/CD GitHub Actions", "descripcion": "Pipeline deploy", "prioridad": "Media", "columna": "Todo"},
    {"titulo": "Escribir tests unitarios backend", "descripcion": "Cubrir auth y scrum", "prioridad": "Media", "columna": "Todo"},
    {"titulo": "Corregir CSS responsive", "descripcion": "Ajustar media queries", "prioridad": "Baja", "columna": "Todo"},
    # Haciendose (4)
    {"titulo": "Implementar drag & drop Kanban", "descripcion": "Usar @dnd-kit", "prioridad": "Alta", "columna": "Haciendose"},
    {"titulo": "Sistema de tickets v2", "descripcion": "Notificaciones email con Resend", "prioridad": "Critica", "columna": "Haciendose"},
    {"titulo": "Integrar modulo fichajes", "descripcion": "Login register timestamp", "prioridad": "Media", "columna": "Haciendose"},
    {"titulo": "Optimizar queries lentas", "descripcion": "Indices y eager loading", "prioridad": "Alta", "columna": "Haciendose"},
    # En revision (4)
    {"titulo": "Documentar API con Swagger", "descripcion": "Descripciones endpoints", "prioridad": "Baja", "columna": "En revision"},
    {"titulo": "Configurar CSP headers", "descripcion": "Seguridad OWASP", "prioridad": "Media", "columna": "En revision"},
    {"titulo": "Revisar permisos multi-tenant", "descripcion": "Aislamiento por company_id", "prioridad": "Alta", "columna": "En revision"},
    {"titulo": "Testing de eliminacion tareas", "descripcion": "Verificar endpoint DELETE", "prioridad": "Media", "columna": "En revision"},
    # Done (3)
    {"titulo": "Login con JWT", "descripcion": "FastAPI + PyJWT", "prioridad": "Critica", "columna": "Done"},
    {"titulo": "Desplegar frontend Hostinger", "descripcion": "Build via FTP", "prioridad": "Alta", "columna": "Done"},
    {"titulo": "Crear BD MySQL Hostinger", "descripcion": "Schema inicial", "prioridad": "Alta", "columna": "Done"},
]


async def seed_15():
    database_url = config.database_url
    engine = create_async_engine(database_url, echo=False)
    Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with Session() as session:
        count_result = await session.execute(select(func.count()).select_from(Tarea))
        existing = count_result.scalar()
        print(f"Tareas existentes: {existing}")

        orden_counter = {}
        total = 0
        for data in TAREAS_15:
            col = data["columna"]
            orden_counter[col] = orden_counter.get(col, 0)
            tarea = Tarea(
                titulo=data["titulo"],
                descripcion=data["descripcion"],
                prioridad=data["prioridad"],
                columna=col,
                orden=orden_counter[col],
                codigo_empresa=3,
            )
            session.add(tarea)
            orden_counter[col] += 1
            total += 1

        await session.commit()
        print(f"{total} tareas de prueba creadas (empresa 3, distribuidas en 4 columnas)")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_15())
