from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ticket import Ticket
from app.schemas.ticket import TicketCreate


async def crear_ticket(db: AsyncSession, data: TicketCreate, codigo_usuario: int = None) -> Ticket:
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
    # Ciclo de vida: nuevo -> respondido (u otros estados como "en curso", "cerrado").
    # Cuando se adjunta una respuesta se marca la fecha para saber cuándo se atendio.
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
    await db.delete(ticket)
    await db.commit()
