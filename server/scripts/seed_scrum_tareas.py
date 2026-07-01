import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import config
from app.models.tarea import Tarea


TAREAS = [
    {"titulo": "Disenar mockups de la landing page", "descripcion": "Crear prototipos en Figma", "prioridad": "Alta", "columna": "Todo"},
    {"titulo": "Implementar login con JWT", "descripcion": "Usar FastAPI + PyJWT", "prioridad": "Critica", "columna": "Haciendose"},
    {"titulo": "Crear BD MySQL en Hostinger", "descripcion": "Configurar schema inicial", "prioridad": "Alta", "columna": "Done"},
    {"titulo": "Configurar CI/CD en GitHub Actions", "descripcion": "Pipeline de deploy frontend", "prioridad": "Media", "columna": "Todo"},
    {"titulo": "Escribir tests unitarios del backend", "descripcion": "Cubrir servicios de auth y scrum", "prioridad": "Media", "columna": "Todo"},
    {"titulo": "Documentar API con Swagger", "descripcion": "Anadir descripciones a endpoints", "prioridad": "Baja", "columna": "En revision"},
    {"titulo": "Corregir errores de CSS responsive", "descripcion": "Ajustar media queries", "prioridad": "Media", "columna": "Todo"},
    {"titulo": "Implementar modulo de fichajes", "descripcion": "CRUD fichajes con admin view", "prioridad": "Alta", "columna": "Done"},
    {"titulo": "Configurar CSP y CORS", "descripcion": "Seguridad headers", "prioridad": "Media", "columna": "Done"},
    {"titulo": "Desplegar frontend en Hostinger", "descripcion": "Subir build via FTP", "prioridad": "Alta", "columna": "Done"},
]


async def seed_tareas():
    database_url = config.database_url
    engine = create_async_engine(database_url, echo=False)
    Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with Session() as session:
        resultado = await session.execute(select(Tarea).limit(1))
        if resultado.scalar_one_or_none():
            print("Ya hay tareas, se omiten las de prueba")
            await engine.dispose()
            return

        total = 0
        for data in TAREAS:
            tarea = Tarea(**data, codigo_empresa=3, orden=total)
            session.add(tarea)
            total += 1

        await session.commit()
        print(f"{total} tareas de prueba creadas (empresa 3)")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_tareas())
