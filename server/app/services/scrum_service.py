from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sprint import Sprint
from app.models.tarea import Tarea
from app.schemas.tarea import TareaCreate, TareaUpdate


async def listar_tareas(db: AsyncSession, codigo_empresa: int, codigo_sprint: int = None) -> list[Tarea]:
    # Filtro multi-tenant: siempre por codigo_empresa
    query = select(Tarea).where(Tarea.codigo_empresa == codigo_empresa)
    if codigo_sprint is not None:
        query = query.where(Tarea.codigo_sprint == codigo_sprint)
    # Ordenamos por columna primero y luego por 'orden' dentro de cada columna
    # para que el frontend reciba las tareas ya ordenadas para el Kanban y no
    # tenga que reordenarlas en cliente tras cada drag & drop
    query = query.order_by(Tarea.columna, Tarea.orden)
    resultado = await db.execute(query)
    return resultado.scalars().all()


async def obtener_tablero(db: AsyncSession, codigo_empresa: int, codigo_sprint: int = None) -> dict:
    tareas = await listar_tareas(db, codigo_empresa, codigo_sprint)
    # Agrupar tareas en las cuatro columnas clásicas de Kanban; el frontend
    # itera sobre estas claves para montar el tablero sin lógica de agrupación
    return {
        "Todo": [t for t in tareas if t.columna == "Todo"],
        "Haciendose": [t for t in tareas if t.columna == "Haciendose"],
        "En revision": [t for t in tareas if t.columna == "En revision"],
        "Done": [t for t in tareas if t.columna == "Done"],
    }


async def crear_tarea(db: AsyncSession, data: TareaCreate, codigo_empresa: int) -> Tarea:
    tarea = Tarea(**data.model_dump(), codigo_empresa=codigo_empresa)
    db.add(tarea)
    await db.commit()
    await db.refresh(tarea)
    return tarea


async def obtener_tarea(db: AsyncSession, codigo_tarea: int, codigo_empresa: int) -> Tarea:
    resultado = await db.execute(
        select(Tarea).where(Tarea.codigo_tarea == codigo_tarea, Tarea.codigo_empresa == codigo_empresa)
    )
    tarea = resultado.scalar_one_or_none()
    if not tarea:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada")
    return tarea


async def actualizar_tarea(db: AsyncSession, codigo_tarea: int, data: TareaUpdate, codigo_empresa: int) -> Tarea:
    tarea = await obtener_tarea(db, codigo_tarea, codigo_empresa)
    for campo, valor in data.model_dump(exclude_unset=True).items():
        setattr(tarea, campo, valor)
    await db.commit()
    await db.refresh(tarea)
    return tarea


async def mover_tarea(db: AsyncSession, codigo_tarea: int, columna: str, orden: int, codigo_empresa: int) -> Tarea:
    # Endpoint específico para drag & drop: actualiza columna Y orden en un solo
    # paso atómico. El frontend calcula el nuevo 'orden' según la posición donde
    # se suelta la tarea, recorriendo las tareas vecinas para asignar un valor
    # secuencial (1, 2, 3...) que el backend acepta sin recalcular nada
    tarea = await obtener_tarea(db, codigo_tarea, codigo_empresa)
    tarea.columna = columna
    tarea.orden = orden
    await db.commit()
    await db.refresh(tarea)
    return tarea


async def eliminar_tarea(db: AsyncSession, codigo_tarea: int, codigo_empresa: int) -> None:
    tarea = await obtener_tarea(db, codigo_tarea, codigo_empresa)
    await db.delete(tarea)
    await db.commit()


async def listar_sprints(db: AsyncSession, codigo_empresa: int, skip: int = 0, limit: int = 50) -> tuple[list[Sprint], int]:
    total = (
        await db.execute(select(func.count(Sprint.codigo_sprint)).where(Sprint.codigo_empresa == codigo_empresa))
    ).scalar()
    resultado = await db.execute(
        select(Sprint).where(Sprint.codigo_empresa == codigo_empresa).order_by(Sprint.codigo_sprint.desc()).offset(skip).limit(limit)
    )
    return resultado.scalars().all(), total


async def crear_sprint(db: AsyncSession, data, codigo_empresa: int) -> Sprint:
    sprint = Sprint(**data.model_dump(), codigo_empresa=codigo_empresa)
    db.add(sprint)
    await db.commit()
    await db.refresh(sprint)
    return sprint


async def obtener_sprint(db: AsyncSession, codigo_sprint: int, codigo_empresa: int) -> Sprint:
    resultado = await db.execute(
        select(Sprint).where(Sprint.codigo_sprint == codigo_sprint, Sprint.codigo_empresa == codigo_empresa)
    )
    sprint = resultado.scalar_one_or_none()
    if not sprint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sprint no encontrado")
    return sprint


async def actualizar_sprint(db: AsyncSession, codigo_sprint: int, data, codigo_empresa: int) -> Sprint:
    sprint = await obtener_sprint(db, codigo_sprint, codigo_empresa)
    for campo, valor in data.model_dump(exclude_unset=True).items():
        setattr(sprint, campo, valor)
    await db.commit()
    await db.refresh(sprint)
    return sprint


async def eliminar_sprint(db: AsyncSession, codigo_sprint: int, codigo_empresa: int) -> None:
    sprint = await obtener_sprint(db, codigo_sprint, codigo_empresa)
    await db.delete(sprint)
    await db.commit()
