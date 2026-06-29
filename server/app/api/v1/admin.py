from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_usuario_actual
from app.models.usuario import Usuario
from app.schemas.admin import (
    EmpresaCreate,
    EmpresaResponse,
    EmpresaUpdate,
    ServicioResponse,
    ServicioToggle,
    UsuarioAdminResponse,
    UsuarioCreate,
    UsuarioUpdate,
)
from app.services import admin_service

router = APIRouter(prefix="/admin", tags=["Admin"])


# ────────────────────────────── EMPRESAS ──────────────────────────────


@router.get("/empresas", response_model=list[EmpresaResponse])
async def listar_empresas(
    usuario: Usuario = Depends(get_usuario_actual),
    db: AsyncSession = Depends(get_db),
):
    if usuario.rol != "admin_total":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para listar empresas",
        )
    return await admin_service.listar_empresas(db)


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
    return await admin_service.crear_empresa(db, body)


@router.get("/empresas/{codigo_empresa}", response_model=EmpresaResponse)
async def obtener_empresa(
    codigo_empresa: int,
    usuario: Usuario = Depends(get_usuario_actual),
    db: AsyncSession = Depends(get_db),
):
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
    await admin_service.eliminar_empresa(db, codigo_empresa)


# ────────────────────────────── USUARIOS ──────────────────────────────


@router.get("/empresas/{codigo_empresa}/usuarios", response_model=list[UsuarioAdminResponse])
async def listar_usuarios_por_empresa(
    codigo_empresa: int,
    usuario: Usuario = Depends(get_usuario_actual),
    db: AsyncSession = Depends(get_db),
):
    _verificar_acceso_empresa(usuario, codigo_empresa)
    return await admin_service.listar_usuarios(db, codigo_empresa=codigo_empresa)


@router.get("/usuarios", response_model=list[UsuarioAdminResponse])
async def listar_usuarios(
    usuario: Usuario = Depends(get_usuario_actual),
    db: AsyncSession = Depends(get_db),
):
    if usuario.rol == "admin_total":
        return await admin_service.listar_usuarios(db)
    return await admin_service.listar_usuarios(db, codigo_empresa=usuario.codigo_empresa)


@router.post("/usuarios", response_model=UsuarioAdminResponse, status_code=status.HTTP_201_CREATED)
async def crear_usuario(
    body: UsuarioCreate,
    usuario: Usuario = Depends(get_usuario_actual),
    db: AsyncSession = Depends(get_db),
):
    if usuario.rol == "admin_total":
        return await admin_service.crear_usuario_admin(db, body)
    if usuario.rol == "admin_empresa" and body.codigo_empresa == usuario.codigo_empresa:
        return await admin_service.crear_usuario_admin(db, body)
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No tienes permisos para crear usuarios en esta empresa",
    )


@router.put("/usuarios/{codigo_usuario}", response_model=UsuarioAdminResponse)
async def actualizar_usuario(
    codigo_usuario: int,
    body: UsuarioUpdate,
    usuario: Usuario = Depends(get_usuario_actual),
    db: AsyncSession = Depends(get_db),
):
    usuario_modificar = await admin_service.obtener_usuario_por_id(db, codigo_usuario)
    if not usuario_modificar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    if usuario.rol == "admin_total":
        return await admin_service.actualizar_usuario(db, codigo_usuario, body)
    if usuario.rol == "admin_empresa" and usuario_modificar.codigo_empresa == usuario.codigo_empresa:
        return await admin_service.actualizar_usuario(db, codigo_usuario, body)
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No tienes permisos para modificar este usuario",
    )


@router.delete("/usuarios/{codigo_usuario}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_usuario(
    codigo_usuario: int,
    usuario: Usuario = Depends(get_usuario_actual),
    db: AsyncSession = Depends(get_db),
):
    usuario_eliminar = await admin_service.obtener_usuario_por_id(db, codigo_usuario)
    if not usuario_eliminar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    if usuario.rol == "admin_total":
        await admin_service.eliminar_usuario(db, codigo_usuario)
        return
    if usuario.rol == "admin_empresa" and usuario_eliminar.codigo_empresa == usuario.codigo_empresa:
        await admin_service.eliminar_usuario(db, codigo_usuario)
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No tienes permisos para eliminar este usuario",
    )


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
    return await admin_service.toggle_servicio(db, codigo_empresa, body)


# ────────────────────────────── UTILS ──────────────────────────────


def _verificar_acceso_empresa(usuario: Usuario, codigo_empresa: int) -> None:
    # Admin total accede a todo; admin_empresa solo a su propia empresa
    if usuario.rol == "admin_total":
        return
    if usuario.rol == "admin_empresa" and usuario.codigo_empresa == codigo_empresa:
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No tienes permisos para acceder a esta empresa",
    )
