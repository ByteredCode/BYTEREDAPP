from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_tenant_filter, require_servicio
from app.core.limiter import limiter
from app.schemas.admin import Paginacion
from app.schemas.tarea import (
    SprintCreate,
    SprintResponse,
    SprintUpdate,
    TareaCreate,
    TareaMover,
    TareaResponse,
    TareaUpdate,
)
from app.services.scrum_service import (
    actualizar_sprint,
    actualizar_tarea,
    crear_sprint,
    crear_tarea,
    eliminar_sprint,
    eliminar_tarea,
    listar_sprints,
    listar_tareas,
    mover_tarea,
    obtener_sprint,
    obtener_tablero,
    obtener_tarea,
)

router = APIRouter(
    prefix="/scrum",
    tags=["Scrum"],
    dependencies=[Depends(require_servicio("scrum"))],
)


@router.get("/tablero")
async def get_tablero(
    codigo_sprint: int = None,
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
):
    # get_tenant_filter extrae el company_id del JWT y lo inyecta automaticamente,
    # asi cada query queda aislada por empresa sin que el endpoint tenga que hacerlo manualmente
    return await obtener_tablero(db, codigo_empresa, codigo_sprint)


@router.get("/tareas", response_model=list[TareaResponse])
async def get_tareas(
    codigo_sprint: int = None,
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
):
    # El parametro opcional codigo_sprint permite filtrar tareas por sprint,
    # util para el tablero kanban que muestra solo las tareas del sprint activo
    return await listar_tareas(db, codigo_empresa, codigo_sprint)


@router.post("/tareas", response_model=TareaResponse, status_code=201)
@limiter.limit("30/minute")
async def post_tarea(
    request: Request,
    data: TareaCreate,
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
):
    return await crear_tarea(db, data, codigo_empresa)


@router.get("/tareas/{codigo_tarea}", response_model=TareaResponse)
async def get_tarea(
    codigo_tarea: int,
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
):
    return await obtener_tarea(db, codigo_tarea, codigo_empresa)


@router.put("/tareas/{codigo_tarea}", response_model=TareaResponse)
async def put_tarea(
    codigo_tarea: int,
    data: TareaUpdate,
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
):
    return await actualizar_tarea(db, codigo_tarea, data, codigo_empresa)


@router.put("/tareas/{codigo_tarea}/mover", response_model=TareaResponse)
async def put_mover_tarea(
    codigo_tarea: int,
    data: TareaMover,
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
):
    # Endpoint exclusivo para drag & drop: separamos el reordenamiento de una
    # actualizacion normal para evitar que el frontend envie datos innecesarios.
    # El servidor recalcula el orden (posicion) entre las tareas vecinas para
    # evitar conflictos de concurrencia al arrastrar.
    return await mover_tarea(db, codigo_tarea, data.columna, data.orden, codigo_empresa)


@router.delete("/tareas/{codigo_tarea}", status_code=204)
@limiter.limit("20/minute")
async def delete_tarea(
    request: Request,
    codigo_tarea: int,
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
):
    await eliminar_tarea(db, codigo_tarea, codigo_empresa)


@router.get("/sprints")
async def get_sprints(
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
    pag: Paginacion = Depends(),
):
    items, total = await listar_sprints(db, codigo_empresa, pag.skip, pag.limit)
    return {"items": items, "total": total}


@router.post("/sprints", response_model=SprintResponse, status_code=201)
@limiter.limit("10/minute")
async def post_sprint(
    request: Request,
    data: SprintCreate,
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
):
    # El tenant se inyecta automaticamente, asi el sprint se asocia a la empresa
    # del usuario autenticado sin que el frontend tenga que enviar el company_id
    return await crear_sprint(db, data, codigo_empresa)


@router.get("/sprints/{codigo_sprint}", response_model=SprintResponse)
async def get_sprint(
    codigo_sprint: int,
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
):
    return await obtener_sprint(db, codigo_sprint, codigo_empresa)


@router.put("/sprints/{codigo_sprint}", response_model=SprintResponse)
async def put_sprint(
    codigo_sprint: int,
    data: SprintUpdate,
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
):
    return await actualizar_sprint(db, codigo_sprint, data, codigo_empresa)


@router.delete("/sprints/{codigo_sprint}", status_code=204)
@limiter.limit("10/minute")
async def delete_sprint(
    request: Request,
    codigo_sprint: int,
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
):
    await eliminar_sprint(db, codigo_sprint, codigo_empresa)
