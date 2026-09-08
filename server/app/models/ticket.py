from sqlalchemy import Column, DateTime, Enum as SAEnum, ForeignKey, Integer, String, Text
from sqlalchemy import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id_reporte = Column(Integer, primary_key=True, autoincrement=True)
    # codigo_usuario = NULL permite tickets de usuarios anónimos (sin autenticación).
    # ondelete="SET NULL" conserva el ticket como histórico aunque el usuario se borre después.
    codigo_usuario = Column(Integer, ForeignKey("usuario.codigo_usuario", ondelete="SET NULL"), nullable=True)
    nombre_contacto = Column(String(150))  # Nombre del remitente si es anónimo
    correo_contacto = Column(String(150))  # Email de contacto si es anónimo
    asunto = Column(String(200))
    # Enum SQL fijo porque los niveles de importancia del ticket son conocidos y acotados
    nivel_importancia = Column(
        SAEnum("Baja", "Media", "Alta", "Critica", name="importancia_enum"),
        nullable=False,
    )
    mensaje = Column(Text, nullable=False)
    # FK al tenant con CASCADE: si la empresa se elimina, todos sus tickets se borran en cascada
    codigo_empresa = Column(Integer, ForeignKey("empresa.codigo_empresa", ondelete="CASCADE"), nullable=False)
    # Enum que define el ciclo de vida del ticket (workflow fijo de atención al cliente)
    estado = Column(
        SAEnum("Pendiente", "Leido", "Respondido", "Cerrado", name="estado_ticket_enum"),
        default="Pendiente",
    )
    # server_default usa la hora del servidor de BD en lugar de la de la aplicación,
    # evitando desincronización entre nodos o husos horarios inconsistentes
    fecha_reporte = Column(DateTime, server_default=func.current_timestamp())
    respuesta = Column(Text)
    fecha_respuesta = Column(DateTime)
    # JSON array de rutas relativas: ["{empresa}/{uuid}.jpg", ...]
    fotos = Column(Text)

    # Relación ORM para navegación bidireccional sin JOINs manuales
    empresa = relationship("Empresa", back_populates="tickets")
