import json
import os
import uuid
import logging
from datetime import datetime, timezone

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ticket import Ticket
from app.models.empresa import Empresa
from app.schemas.ticket import TicketCreate

logger = logging.getLogger(__name__)

DIRECTORIO_UPLOADS = os.environ.get(
    "UPLOADS_DIR",
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads"),
)

FOTOS_TIPOS_PERMITIDOS = {"image/jpeg", "image/png", "image/gif", "image/webp"}
FOTOS_MAX_TAMANO = 5 * 1024 * 1024  # 5 MB
FOTOS_MAX_CANTIDAD = 3


async def guardar_fotos(
    ticket: Ticket, fotos: list[UploadFile], codigo_empresa: int, db: AsyncSession
) -> None:
    if not fotos:
        return

    if len(fotos) > FOTOS_MAX_CANTIDAD:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximo {FOTOS_MAX_CANTIDAD} fotos por ticket",
        )

    rutas = []
    directorio = os.path.join(DIRECTORIO_UPLOADS, str(codigo_empresa), "tickets")
    os.makedirs(directorio, exist_ok=True)

    for foto in fotos:
        if foto.content_type and foto.content_type not in FOTOS_TIPOS_PERMITIDOS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo no permitido: {foto.content_type}. Usa JPEG, PNG, GIF o WebP",
            )

        contenido = await foto.read()
        if len(contenido) > FOTOS_MAX_TAMANO:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La foto {foto.filename} supera 5 MB",
            )

        ext = os.path.splitext(foto.filename or "")[1].lower() or ".jpg"
        nombre = f"{uuid.uuid4().hex}{ext}"
        ruta_completa = os.path.join(directorio, nombre)

        with open(ruta_completa, "wb") as f:
            f.write(contenido)

        rutas.append(f"{codigo_empresa}/tickets/{nombre}")
        logger.info(f"Foto ticket guardada: {ruta_completa} ({len(contenido)} bytes)")

    ticket.fotos = json.dumps(rutas)
    await db.commit()
    await db.refresh(ticket)


def eliminar_fotos_ticket(ticket: Ticket) -> None:
    if not ticket.fotos:
        return
    try:
        rutas = json.loads(ticket.fotos)
    except (json.JSONDecodeError, TypeError):
        return
    for ruta in rutas:
        completa = os.path.join(DIRECTORIO_UPLOADS, ruta)
        try:
            if os.path.exists(completa):
                os.remove(completa)
                logger.info(f"Foto ticket eliminada: {completa}")
        except OSError as e:
            logger.error(f"Error eliminando foto {completa}: {e}")


def leer_foto_bytes(ruta_relativa: str) -> bytes:
    completa = os.path.join(DIRECTORIO_UPLOADS, ruta_relativa)
    if not os.path.exists(completa):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Foto no encontrada")
    with open(completa, "rb") as f:
        return f.read()


def obtener_fotos_adjuntos(ticket: Ticket) -> list[tuple[str, bytes]]:
    """Devuelve pares (nombre_archivo, bytes) para adjuntar al email."""
    if not ticket.fotos:
        return []
    try:
        rutas = json.loads(ticket.fotos)
    except (json.JSONDecodeError, TypeError):
        return []
    adjuntos = []
    for ruta in rutas:
        completa = os.path.join(DIRECTORIO_UPLOADS, ruta)
        if os.path.exists(completa):
            nombre = os.path.basename(ruta)
            with open(completa, "rb") as f:
                adjuntos.append((nombre, f.read()))
    return adjuntos


async def crear_ticket(db: AsyncSession, data: TicketCreate, codigo_usuario: int = None) -> Ticket:
    existe = await db.execute(
        select(Empresa).where(Empresa.codigo_empresa == data.codigo_empresa).limit(1)
    )
    if not existe.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Empresa no válida")

    ticket = Ticket(
        codigo_usuario=codigo_usuario,
        nombre_contacto=data.nombre_contacto,
        correo_contacto=data.correo_contacto,
        asunto=data.asunto,
        nivel_importancia=data.nivel_importancia,
        mensaje=data.mensaje,
        codigo_empresa=data.codigo_empresa,
    )
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)
    return ticket


async def listar_tickets(db: AsyncSession, codigo_empresa: int, skip: int = 0, limit: int = 50) -> tuple[list[Ticket], int]:
    total = (
        await db.execute(select(func.count(Ticket.id_reporte)).where(Ticket.codigo_empresa == codigo_empresa))
    ).scalar()
    resultado = await db.execute(
        select(Ticket).where(Ticket.codigo_empresa == codigo_empresa).order_by(Ticket.fecha_reporte.desc()).offset(skip).limit(limit)
    )
    return resultado.scalars().all(), total


async def obtener_ticket(db: AsyncSession, id_reporte: int, codigo_empresa: int) -> Ticket:
    resultado = await db.execute(
        select(Ticket).where(Ticket.id_reporte == id_reporte, Ticket.codigo_empresa == codigo_empresa)
    )
    ticket = resultado.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket no encontrado")
    return ticket


async def actualizar_estado_ticket(
    db: AsyncSession, id_reporte: int, estado: str, codigo_empresa: int, respuesta: str | None = None
) -> Ticket:
    ticket = await obtener_ticket(db, id_reporte, codigo_empresa)
    ticket.estado = estado
    if respuesta:
        ticket.respuesta = respuesta
        ticket.fecha_respuesta = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(ticket)
    return ticket


async def eliminar_ticket(db: AsyncSession, id_reporte: int, codigo_empresa: int) -> None:
    ticket = await obtener_ticket(db, id_reporte, codigo_empresa)
    eliminar_fotos_ticket(ticket)
    await db.delete(ticket)
    await db.commit()
