import os
import uuid
import logging
from datetime import date

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.documento import Documento
from app.models.documento_permiso import DocumentoPermiso

logger = logging.getLogger(__name__)

DIRECTORIO_UPLOADS = os.environ.get("UPLOADS_DIR", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads"))

TIPOS_PERMITIDOS = {
    "application/pdf",
    "image/jpeg", "image/png", "image/gif",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "text/plain",
}
MAX_TAMANO = 10 * 1024 * 1024


async def subir_documento(
    db: AsyncSession, archivo: UploadFile, tipo_documento: str, codigo_empresa: int, usuario_subio: int
) -> Documento:
    logger.info(f"Subiendo documento: {archivo.filename} (tipo: {archivo.content_type}, empresa: {codigo_empresa})")

    if archivo.content_type and archivo.content_type not in TIPOS_PERMITIDOS:
        logger.warning(f"Tipo no permitido: {archivo.content_type}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de archivo no permitido: {archivo.content_type}",
        )
    ext_permitidas = {".pdf", ".jpg", ".jpeg", ".png", ".gif", ".doc", ".docx", ".xls", ".xlsx", ".txt"}
    ext = os.path.splitext(archivo.filename)[1].lower() if archivo.filename else ""
    if ext and ext not in ext_permitidas:
        logger.warning(f"Extension no permitida: {ext}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Extension no permitida: {ext}",
        )

    try:
        os.makedirs(os.path.join(DIRECTORIO_UPLOADS, str(codigo_empresa)), exist_ok=True)
        logger.info(f"Directorio uploads: {DIRECTORIO_UPLOADS}/{codigo_empresa}")
    except OSError as e:
        logger.error(f"Error creando directorio uploads: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear directorio de almacenamiento: {e}",
        )

    nombre_unico = f"{uuid.uuid4().hex}{ext}"
    ruta_relativa = os.path.join(str(codigo_empresa), nombre_unico)
    ruta_completa = os.path.join(DIRECTORIO_UPLOADS, ruta_relativa)

    try:
        contenido = await archivo.read()
    except Exception as e:
        logger.error(f"Error leyendo archivo: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al leer el archivo: {e}",
        )

    if len(contenido) > MAX_TAMANO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo supera el tamano maximo de 10MB",
        )

    try:
        with open(ruta_completa, "wb") as f:
            f.write(contenido)
        logger.info(f"Archivo guardado: {ruta_completa} ({len(contenido)} bytes)")
    except OSError as e:
        logger.error(f"Error escribiendo archivo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al guardar el archivo en disco: {e}",
        )

    doc = Documento(
        nombre=archivo.filename or "sin_nombre",
        codigo_empresa=codigo_empresa,
        usuario_subio=usuario_subio,
        fecha=date.today(),
        ruta_archivo=ruta_relativa,
        tipo_documento=tipo_documento if tipo_documento else None,
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return doc


async def listar_documentos(db: AsyncSession, codigo_empresa: int, usuario_id: int, es_admin: bool, skip: int = 0, limit: int = 50) -> tuple[list[Documento], int]:
    base = select(Documento).where(Documento.codigo_empresa == codigo_empresa)
    if not es_admin:
        subquery = (
            select(DocumentoPermiso.id_documento).where(DocumentoPermiso.codigo_usuario == usuario_id)
        ).subquery()
        base = base.where(
            (Documento.usuario_subio == usuario_id) | (Documento.id_documento.in_(select(subquery)))
        )
    total = (await db.execute(select(func.count()).select_from(base.subquery()))).scalar()
    query = base.order_by(Documento.fecha.desc()).offset(skip).limit(limit)
    resultado = await db.execute(query)
    return resultado.scalars().all(), total


async def obtener_documento(db: AsyncSession, id_documento: int, codigo_empresa: int) -> Documento:
    resultado = await db.execute(
        select(Documento).where(Documento.id_documento == id_documento, Documento.codigo_empresa == codigo_empresa)
    )
    doc = resultado.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento no encontrado")
    return doc


async def eliminar_documento(db: AsyncSession, id_documento: int, codigo_empresa: int) -> None:
    doc = await obtener_documento(db, id_documento, codigo_empresa)
    ruta = os.path.join(DIRECTORIO_UPLOADS, doc.ruta_archivo) if doc.ruta_archivo else None
    if ruta and os.path.exists(ruta):
        os.remove(ruta)
    await db.delete(doc)
    await db.commit()


async def listar_permisos(db: AsyncSession, id_documento: int, codigo_empresa: int) -> list[DocumentoPermiso]:
    await obtener_documento(db, id_documento, codigo_empresa)
    resultado = await db.execute(
        select(DocumentoPermiso).where(DocumentoPermiso.id_documento == id_documento)
    )
    return resultado.scalars().all()


async def agregar_permiso(db: AsyncSession, id_documento: int, codigo_usuario: int, codigo_empresa: int, usuario_actual: int, es_admin: bool) -> DocumentoPermiso:
    doc = await obtener_documento(db, id_documento, codigo_empresa)
    if not es_admin and doc.usuario_subio != usuario_actual:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para gestionar permisos de este documento",
        )
    permiso = DocumentoPermiso(id_documento=id_documento, codigo_usuario=codigo_usuario)
    db.add(permiso)
    try:
        await db.commit()
        await db.refresh(permiso)
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El permiso ya existe")
    return permiso


async def quitar_permiso(db: AsyncSession, id_documento: int, codigo_usuario: int, codigo_empresa: int, usuario_actual: int, es_admin: bool) -> None:
    doc = await obtener_documento(db, id_documento, codigo_empresa)
    if not es_admin and doc.usuario_subio != usuario_actual:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para gestionar permisos de este documento",
        )
    resultado = await db.execute(
        select(DocumentoPermiso).where(
            DocumentoPermiso.id_documento == id_documento, DocumentoPermiso.codigo_usuario == codigo_usuario
        )
    )
    permiso = resultado.scalar_one_or_none()
    if not permiso:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permiso no encontrado")
    await db.delete(permiso)
    await db.commit()


async def obtener_ruta_archivo(doc: Documento) -> str:
    ruta = os.path.join(DIRECTORIO_UPLOADS, doc.ruta_archivo) if doc.ruta_archivo else None
    if not ruta or not os.path.exists(ruta):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archivo no encontrado en el servidor")
    return ruta
