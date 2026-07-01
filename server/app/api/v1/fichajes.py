from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_tenant_filter, get_usuario_actual
from app.models.usuario import Usuario
from app.schemas.admin import Paginacion
from app.schemas.fichaje import FichajeAdminResponse, FichajeResumenResponse, FichajeResponse
from app.services.fichaje_service import (
    fichaje_abierto,
    generar_csv,
    listar_fichajes,
    listar_fichajes_admin,
    obtener_resumen,
    registrar_entrada,
    registrar_salida,
)

router = APIRouter(prefix="/fichajes", tags=["Fichajes"])


@router.get("")
async def get_fichajes(
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
    usuario: Usuario = Depends(get_usuario_actual),
    pag: Paginacion = Depends(),
    empresa_filtro: Optional[int] = Query(None, description="Filtrar por empresa (solo admin_total)"),
):
    # Los administradores ven fichajes de todos los usuarios de su ambito,
    # mientras que los usuarios regulares solo ven sus propios fichajes.
    if usuario.rol == "admin_total":
        filtro = empresa_filtro if empresa_filtro is not None else None
        items, total = await listar_fichajes_admin(db, filtro, pag.skip, pag.limit)
        return {"items": items, "total": total}
    elif usuario.rol == "admin_empresa":
        items, total = await listar_fichajes_admin(db, codigo_empresa, pag.skip, pag.limit)
        return {"items": items, "total": total}
    else:
        items, total = await listar_fichajes(db, usuario.codigo_usuario, codigo_empresa, pag.skip, pag.limit)
        return {"items": items, "total": total}


@router.get("/actual", response_model=FichajeResponse)
async def get_actual(
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
    usuario: Usuario = Depends(get_usuario_actual),
):
    # Endpoint específico para saber si el usuario tiene un fichaje abierto,
    # útil para que el frontend muestre el botón de "Entrada" o "Salida"
    fichaje = await fichaje_abierto(db, usuario.codigo_usuario, codigo_empresa)
    if not fichaje:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No hay fichaje abierto")
    return fichaje


@router.get("/resumen", response_model=FichajeResumenResponse)
async def get_resumen(
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
    usuario: Usuario = Depends(get_usuario_actual),
):
    return await obtener_resumen(db, usuario.codigo_usuario, codigo_empresa)


@router.get("/exportar")
async def get_exportar(
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
    usuario: Usuario = Depends(get_usuario_actual),
    empresa_filtro: Optional[int] = Query(None, description="Filtrar por empresa (solo admin_total)"),
):
    if usuario.rol == "admin_total":
        filtro = empresa_filtro if empresa_filtro is not None else None
        fichajes, _ = await listar_fichajes_admin(db, filtro, limit=99999)
    elif usuario.rol == "admin_empresa":
        fichajes, _ = await listar_fichajes_admin(db, codigo_empresa, limit=99999)
    else:
        fichajes, _ = await listar_fichajes(db, usuario.codigo_usuario, codigo_empresa, limit=99999)
    csv = generar_csv(fichajes)
    return PlainTextResponse(
        content=csv,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=fichajes.csv"},
    )


@router.post("/entrada", response_model=FichajeResponse, status_code=201)
async def post_entrada(
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
    usuario: Usuario = Depends(get_usuario_actual),
):
    existe = await fichaje_abierto(db, usuario.codigo_usuario, codigo_empresa)
    if existe:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya tienes un fichaje abierto")
    return await registrar_entrada(db, usuario.codigo_usuario, codigo_empresa)


@router.post("/salida", response_model=FichajeResponse)
async def post_salida(
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
    usuario: Usuario = Depends(get_usuario_actual),
):
    return await registrar_salida(db, usuario.codigo_usuario, codigo_empresa)
