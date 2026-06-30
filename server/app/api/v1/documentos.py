from fastapi import APIRouter, Depends, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_tenant_filter, get_usuario_actual
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

router = APIRouter(prefix="/documentos", tags=["Documentos"])


@router.post("", response_model=DocumentoResponse, status_code=201)
async def post_documento(
    # UploadFile y Form se usan juntos para recibir multipart/form-data,
    # necesario porque el archivo binario y los metadatos viajan en la misma petición
    archivo: UploadFile = File(...),
    tipo_documento: str = Form(default=None),
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
    usuario: Usuario = Depends(get_usuario_actual),
):
    return await subir_documento(db, archivo, tipo_documento, codigo_empresa, usuario.codigo_usuario)


@router.get("")
async def get_documentos(
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
    usuario: Usuario = Depends(get_usuario_actual),
    pag: Paginacion = Depends(),
):
    es_admin = usuario.rol in ("admin_total", "admin_empresa")
    items, total = await listar_documentos(db, codigo_empresa, usuario.codigo_usuario, es_admin, pag.skip, pag.limit)
    return {"items": items, "total": total}


@router.get("/{id_documento}", response_model=DocumentoResponse)
async def get_documento(
    id_documento: int,
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
):
    return await obtener_documento(db, id_documento, codigo_empresa)


@router.get("/{id_documento}/descargar")
async def descargar_documento(
    id_documento: int,
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
):
    # Primero se obtiene el documento (con verificación de tenant) para confirmar
    # que existe y pertenece a la empresa; luego se resuelve la ruta física del archivo
    doc = await obtener_documento(db, id_documento, codigo_empresa)
    ruta = await obtener_ruta_archivo(doc)
    return FileResponse(ruta, filename=doc.nombre, media_type="application/octet-stream")


@router.delete("/{id_documento}", status_code=204)
async def delete_documento(
    id_documento: int,
    db: AsyncSession = Depends(get_db),
    codigo_empresa: int = Depends(get_tenant_filter),
):
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
