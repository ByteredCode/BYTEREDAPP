import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_usuario_actual
from app.models.usuario import Usuario
from app.schemas.admin import (
    AdminStatsResponse,
    EmpresaCreate,
    EmpresaResponse,
    EmpresaUpdate,
    Paginacion,
    ServicioResponse,
    ServicioToggle,
    UsuarioAdminResponse,
    UsuarioCreate,
    UsuarioUpdate,
)
from app.services import admin_service

router = APIRouter(prefix="/admin", tags=["Admin"])
logger = logging.getLogger("byteredapp.admin")


# ────────────────────────────── EMPRESAS ──────────────────────────────


@router.get("/empresas")
async def listar_empresas(
    pag: Paginacion = Depends(),
    usuario: Usuario = Depends(get_usuario_actual),
    db: AsyncSession = Depends(get_db),
):
    if usuario.rol != "admin_total":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para listar empresas",
        )
    items, total = await admin_service.listar_empresas(db, pag.skip, pag.limit)
    return {"items": items, "total": total}


@router.post("/empresas", response_model=EmpresaResponse, status_code=status.HTTP_201_CREATED)
async def crear_empresa(
    body: EmpresaCreate,
    usuario: Usuario = Depends(get_usuario_actual),
    db: AsyncSession = Depends(get_db),
):
    if usuario.rol != "admin_total":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para crear empresas",
        )
    empresa = await admin_service.crear_empresa(db, body)
    logger.info("Admin %s creo empresa %s (%s)", usuario.codigo_usuario, empresa.codigo_empresa, empresa.nombre)
    return empresa


@router.get("/empresas/{codigo_empresa}", response_model=EmpresaResponse)
async def obtener_empresa(
    codigo_empresa: int,
    usuario: Usuario = Depends(get_usuario_actual),
    db: AsyncSession = Depends(get_db),
):
    # La funcion _verificar_acceso_empresa centraliza la logica de permisos:
    # admin_total ve todo, admin_empresa solo su propia empresa
    _verificar_acceso_empresa(usuario, codigo_empresa)
    empresa = await admin_service.obtener_empresa(db, codigo_empresa)
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa no encontrada",
        )
    return empresa


@router.put("/empresas/{codigo_empresa}", response_model=EmpresaResponse)
async def actualizar_empresa(
    codigo_empresa: int,
    body: EmpresaUpdate,
    usuario: Usuario = Depends(get_usuario_actual),
    db: AsyncSession = Depends(get_db),
):
    if usuario.rol != "admin_total":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para actualizar empresas",
        )
    return await admin_service.actualizar_empresa(db, codigo_empresa, body)


@router.delete("/empresas/{codigo_empresa}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_empresa(
    codigo_empresa: int,
    usuario: Usuario = Depends(get_usuario_actual),
    db: AsyncSession = Depends(get_db),
):
    if usuario.rol != "admin_total":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para eliminar empresas",
        )
    logger.warning("Admin %s elimino empresa %s", usuario.codigo_usuario, codigo_empresa)
    await admin_service.eliminar_empresa(db, codigo_empresa)


# ────────────────────────────── USUARIOS ──────────────────────────────


@router.get("/empresas/{codigo_empresa}/usuarios")
async def listar_usuarios_por_empresa(
    codigo_empresa: int,
    pag: Paginacion = Depends(),
    usuario: Usuario = Depends(get_usuario_actual),
    db: AsyncSession = Depends(get_db),
):
    if usuario.rol != "admin_total":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el administrador principal puede gestionar usuarios",
        )
    items, total = await admin_service.listar_usuarios(db, codigo_empresa=codigo_empresa, skip=pag.skip, limit=pag.limit)
    return {"items": items, "total": total}


@router.get("/usuarios")
async def listar_usuarios(
    pag: Paginacion = Depends(),
    usuario: Usuario = Depends(get_usuario_actual),
    db: AsyncSession = Depends(get_db),
):
    if usuario.rol != "admin_total":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el administrador principal puede gestionar usuarios",
        )
    items, total = await admin_service.listar_usuarios(db, skip=pag.skip, limit=pag.limit)
    return {"items": items, "total": total}


@router.post("/usuarios", response_model=UsuarioAdminResponse, status_code=status.HTTP_201_CREATED)
async def crear_usuario(
    body: UsuarioCreate,
    usuario: Usuario = Depends(get_usuario_actual),
    db: AsyncSession = Depends(get_db),
):
    if usuario.rol != "admin_total":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el administrador principal puede crear usuarios",
        )
    nuevo = await admin_service.crear_usuario_admin(db, body)
    logger.info("Admin %s creo usuario %s (%s) en empresa %s con rol %s", usuario.codigo_usuario, nuevo.codigo_usuario, nuevo.correo, body.codigo_empresa, body.rol)
    return nuevo


@router.put("/usuarios/{codigo_usuario}", response_model=UsuarioAdminResponse)
async def actualizar_usuario(
    codigo_usuario: int,
    body: UsuarioUpdate,
    usuario: Usuario = Depends(get_usuario_actual),
    db: AsyncSession = Depends(get_db),
):
    if usuario.rol != "admin_total":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el administrador principal puede modificar usuarios",
        )
    actualizado = await admin_service.actualizar_usuario(db, codigo_usuario, body)
    logger.info("Admin %s actualizo usuario %s — campos: %s", usuario.codigo_usuario, codigo_usuario, list(body.model_dump(exclude_unset=True).keys()))
    return actualizado


@router.delete("/usuarios/{codigo_usuario}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_usuario(
    codigo_usuario: int,
    usuario: Usuario = Depends(get_usuario_actual),
    db: AsyncSession = Depends(get_db),
):
    if usuario.rol != "admin_total":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el administrador principal puede eliminar usuarios",
        )
    logger.warning("Admin %s elimino usuario %s", usuario.codigo_usuario, codigo_usuario)
    await admin_service.eliminar_usuario(db, codigo_usuario)


# ────────────────────────────── SERVICIOS ──────────────────────────────


@router.get("/empresas/{codigo_empresa}/servicios", response_model=list[ServicioResponse])
async def listar_servicios(
    codigo_empresa: int,
    usuario: Usuario = Depends(get_usuario_actual),
    db: AsyncSession = Depends(get_db),
):
    _verificar_acceso_empresa(usuario, codigo_empresa)
    return await admin_service.listar_servicios(db, codigo_empresa)


@router.put("/empresas/{codigo_empresa}/servicios", response_model=ServicioResponse)
async def toggle_servicio(
    codigo_empresa: int,
    body: ServicioToggle,
    usuario: Usuario = Depends(get_usuario_actual),
    db: AsyncSession = Depends(get_db),
):
    if usuario.rol != "admin_total":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para modificar servicios",
        )
    resultado = await admin_service.toggle_servicio(db, codigo_empresa, body)
    logger.info("Admin %s togglo servicio %s de empresa %s a activo=%s", usuario.codigo_usuario, body.servicio, codigo_empresa, body.activo)
    return resultado


# ────────────────────────────── ESTADISTICAS ──────────────────────────────


@router.get("/stats", response_model=AdminStatsResponse)
# Endpoint independiente para estadisticas: se separa de los CRUD para no acoplar
# consultas pesadas de agregacion con operaciones de escritura de datos
async def obtener_stats(
    usuario: Usuario = Depends(get_usuario_actual),
    db: AsyncSession = Depends(get_db),
):
    # admin_total ve estadisticas globales; admin_empresa solo las de su empresa
    codigo_empresa = None if usuario.rol == "admin_total" else usuario.codigo_empresa
    return await admin_service.obtener_stats(db, codigo_empresa)


# ────────────────────────────── UTILS ──────────────────────────────


def _verificar_acceso_empresa(usuario: Usuario, codigo_empresa: int) -> None:
    # Funcion utilitaria que abstrae la comprobacion de permisos por empresa.
    # Asi evitamos repetir el mismo if/raise en todos los endpoints que operan sobre una empresa.
    if usuario.rol == "admin_total":
        return
    if usuario.rol == "admin_empresa" and usuario.codigo_empresa == codigo_empresa:
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No tienes permisos para acceder a esta empresa",
    )
