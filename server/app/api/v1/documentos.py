from typing import Optional
import os
import logging

from fastapi import APIRouter, Depends, Query, Request, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_tenant_filter, get_usuario_actual, require_servicio
from app.core.limiter import limiter
from app.models.usuario import Usuario
from app.schemas.admin import Paginacion
from app.schemas.documento import DocumentoResponse, PermisoAgregar, PermisoResponse
from app.services.documento_service import (
    agregar_permiso,
    eliminar_documento,
    listar_documentos,
    listar_permisos,
    obtener_documento,
    obtener_ruta_archivo,
    quitar_permiso,
    subir_documento,
)

router = APIRouter(
    prefix="/documentos",
    tags=["Documentos"],
    dependencies=[Depends(require_servicio("documentacion"))],
)
logger = logging.getLogger(__name__)


@router.post("", response_model=DocumentoResponse, status_code=201)
@limiter.limit("20/hour")
async def post_documento(
    request: Request,
    archivo: UploadFile = File(...),
    tipo_documento: str = Form(default=None),
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
    usuario: Usuario = Depends(get_usuario_actual),
):
    logger.info(f"Upload request: archivo={archivo.filename}, tipo={tipo_documento}, empresa={codigo_empresa}, usuario={usuario.codigo_usuario}")
    try:
        return await subir_documento(db, archivo, tipo_documento, codigo_empresa, usuario.codigo_usuario)
    except Exception as e:
        logger.error(f"Error en upload: {type(e).__name__}: {e}")
        raise


@router.get("")
async def get_documentos(
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
    usuario: Usuario = Depends(get_usuario_actual),
    pag: Paginacion = Depends(),
    empresa_filtro: Optional[int] = Query(None, description="Filtrar por empresa (solo admin_total)"),
):
    es_admin = usuario.rol in ("admin_total", "admin_empresa")
    filtro = empresa_filtro if (usuario.rol == "admin_total" and empresa_filtro is not None) else codigo_empresa
    items, total = await listar_documentos(db, filtro, usuario.codigo_usuario, es_admin, pag.skip, pag.limit)
    return {"items": items, "total": total}


@router.get("/{id_documento}", response_model=DocumentoResponse)
async def get_documento(
    id_documento: int,
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
    usuario: Usuario = Depends(get_usuario_actual),
):
    doc = await obtener_documento(db, id_documento, codigo_empresa)
    es_admin = usuario.rol in ("admin_total", "admin_empresa")
    if not es_admin and doc.usuario_subio != usuario.codigo_usuario:
        from sqlalchemy import select as sa_select
        from app.models.documento import DocumentoPermiso
        permiso = await db.execute(
            sa_select(DocumentoPermiso).where(
                DocumentoPermiso.id_documento == id_documento,
                DocumentoPermiso.codigo_usuario == usuario.codigo_usuario,
            ).limit(1)
        )
        if not permiso.scalar_one_or_none():
            from fastapi import HTTPException
            raise HTTPException(status_code=403, detail="No tienes acceso a este documento")
    return doc


MIME_TYPES = {
    ".pdf": "application/pdf",
    ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".png": "image/png", ".gif": "image/gif",
    ".doc": "application/msword",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".xls": "application/vnd.ms-excel",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".txt": "text/plain",
}


@router.get("/{id_documento}/descargar")
async def descargar_documento(
    id_documento: int,
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
    usuario: Usuario = Depends(get_usuario_actual),
):
    doc = await obtener_documento(db, id_documento, codigo_empresa)
    es_admin = usuario.rol in ("admin_total", "admin_empresa")
    if not es_admin and doc.usuario_subio != usuario.codigo_usuario:
        from sqlalchemy import select as sa_select
        from app.models.documento import DocumentoPermiso
        permiso = await db.execute(
            sa_select(DocumentoPermiso).where(
                DocumentoPermiso.id_documento == id_documento,
                DocumentoPermiso.codigo_usuario == usuario.codigo_usuario,
            ).limit(1)
        )
        if not permiso.scalar_one_or_none():
            from fastapi import HTTPException
            raise HTTPException(status_code=403, detail="No tienes acceso a este documento")
    ruta = await obtener_ruta_archivo(doc)
    ext = os.path.splitext(doc.nombre)[1].lower() if doc.nombre else ""
    media_type = MIME_TYPES.get(ext, "application/octet-stream")
    return FileResponse(ruta, filename=doc.nombre, media_type=media_type)


@router.delete("/{id_documento}", status_code=204)
async def delete_documento(
    id_documento: int,
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
    usuario: Usuario = Depends(get_usuario_actual),
):
    doc = await obtener_documento(db, id_documento, codigo_empresa)
    es_admin = usuario.rol in ("admin_total", "admin_empresa")
    if not es_admin and doc.usuario_subio != usuario.codigo_usuario:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar este documento")
    await eliminar_documento(db, id_documento, codigo_empresa)


@router.get("/{id_documento}/permisos", response_model=list[PermisoResponse])
async def get_permisos(
    id_documento: int,
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
):
    return await listar_permisos(db, id_documento, codigo_empresa)


@router.post("/{id_documento}/permisos", response_model=PermisoResponse, status_code=201)
async def post_permiso(
    id_documento: int,
    data: PermisoAgregar,
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
    usuario: Usuario = Depends(get_usuario_actual),
):
    # Solo admins o el propietario del documento pueden conceder acceso a otros usuarios;
    # el flag es_admin se pasa al servicio para que valide la política de negocio
    es_admin = usuario.rol in ("admin_total", "admin_empresa")
    return await agregar_permiso(db, id_documento, data.codigo_usuario, codigo_empresa, usuario.codigo_usuario, es_admin)


@router.delete("/{id_documento}/permisos/{codigo_usuario}", status_code=204)
async def delete_permiso(
    id_documento: int,
    codigo_usuario: int,
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
    usuario: Usuario = Depends(get_usuario_actual),
):
    # Misma lógica de permisos que en el POST: solo quien tiene privilegios
    # puede revocar el acceso de otro usuario al documento
    es_admin = usuario.rol in ("admin_total", "admin_empresa")
    await quitar_permiso(db, id_documento, codigo_usuario, codigo_empresa, usuario.codigo_usuario, es_admin)
