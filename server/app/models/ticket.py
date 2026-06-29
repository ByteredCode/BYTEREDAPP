from sqlalchemy import Column, DateTime, Enum as SAEnum, ForeignKey, Integer, String, Text
from sqlalchemy import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id_reporte = Column(Integer, primary_key=True, autoincrement=True)
    # codigo_usuario nullable permite tickets de usuarios anonimos (sin auth)
    codigo_usuario = Column(Integer, ForeignKey("usuario.codigo_usuario", ondelete="SET NULL"), nullable=True)
    nombre_contacto = Column(String(150))  # Nombre del remitente si es anonimo
    correo_contacto = Column(String(150))  # Email de contacto si es anonimo
    asunto = Column(String(200))
    nivel_importancia = Column(
        SAEnum("Baja", "Media", "Alta", "Critica", name="importancia_enum"),
        nullable=False,
    )
    mensaje = Column(Text, nullable=False)
    codigo_empresa = Column(Integer, ForeignKey("empresa.codigo_empresa", ondelete="CASCADE"), nullable=False)
    estado = Column(
        SAEnum("Pendiente", "Leido", "Respondido", "Cerrado", name="estado_ticket_enum"),
        default="Pendiente",
    )
    fecha_reporte = Column(DateTime, server_default=func.current_timestamp())
    respuesta = Column(Text)
    fecha_respuesta = Column(DateTime)

    empresa = relationship("Empresa", back_populates="tickets")
