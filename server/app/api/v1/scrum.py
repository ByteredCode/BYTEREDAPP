from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_tenant_filter
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

router = APIRouter(prefix="/scrum", tags=["Scrum"])


@router.get("/tablero")
async def get_tablero(
    codigo_sprint: int = None,
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
):
    # get_tenant_filter inyecta automaticamente el company_id del JWT
    return await obtener_tablero(db, codigo_empresa, codigo_sprint)


@router.get("/tareas", response_model=list[TareaResponse])
async def get_tareas(
    codigo_sprint: int = None,
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
):
    return await listar_tareas(db, codigo_empresa, codigo_sprint)


@router.post("/tareas", response_model=TareaResponse, status_code=201)
async def post_tarea(
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
    # Endpoint especifico para drag & drop: solo cambia columna y orden
    return await mover_tarea(db, codigo_tarea, data.columna, data.orden, codigo_empresa)


@router.delete("/tareas/{codigo_tarea}", status_code=204)
async def delete_tarea(
    codigo_tarea: int,
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
):
    await eliminar_tarea(db, codigo_tarea, codigo_empresa)


@router.get("/sprints", response_model=list[SprintResponse])
async def get_sprints(
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
):
    return await listar_sprints(db, codigo_empresa)


@router.post("/sprints", response_model=SprintResponse, status_code=201)
async def post_sprint(
    data: SprintCreate,
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
):
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
async def delete_sprint(
    codigo_sprint: int,
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
):
    await eliminar_sprint(db, codigo_sprint, codigo_empresa)
