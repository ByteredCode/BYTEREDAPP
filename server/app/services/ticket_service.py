import logging
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import config
from app.models.ticket import Ticket
from app.schemas.ticket import TicketCreate
from app.services.email_service import enviar_correo

logger = logging.getLogger(__name__)


async def crear_ticket(db: AsyncSession, data: TicketCreate, codigo_usuario: int = None) -> Ticket:
    # El ticket nace en estado "nuevo" por defecto en la BD
    ticket = Ticket(
        codigo_usuario=codigo_usuario,  # None si es ticket anonimo
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

    # Solo se notifica por email si hay una direccion configurada; asi cada empresa
    # decide si quiere alertas por correo o solo consultar el panel
    asunto_email = f"Nuevo ticket: {ticket.asunto or 'Sin asunto'} ({ticket.nivel_importancia})"
    cuerpo = (
        f"Nuevo ticket #{ticket.id_reporte}\n\n"
        f"Nombre: {ticket.nombre_contacto or 'Anonimo'}\n"
        f"Correo: {ticket.correo_contacto}\n"
        f"Empresa: {ticket.codigo_empresa}\n"
        f"Importancia: {ticket.nivel_importancia}\n\n"
        f"Mensaje:\n{ticket.mensaje}"
    )
    if config.TICKETS_EMAIL:
        logger.info(f"Enviando email ticket #{ticket.id_reporte} a {config.TICKETS_EMAIL} via {config.SMTP_HOST}:{config.SMTP_PORT}")
        try:
            enviado = await enviar_correo(config.TICKETS_EMAIL, asunto_email, cuerpo)
            if enviado:
                logger.info(f"Email ticket #{ticket.id_reporte} enviado correctamente")
            else:
                logger.warning(f"Email ticket #{ticket.id_reporte} fallo al enviar (revisar logs SMTP)")
        except Exception as e:
            logger.error(f"Excepcion enviando email ticket #{ticket.id_reporte}: {e}")
    else:
        logger.warning("TICKETS_EMAIL no configurado — email no enviado")

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
