from sqlalchemy import Column, Date, Enum as SAEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class Sprint(Base):
    __tablename__ = "sprints"

    codigo_sprint = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(150), nullable=False)
    objetivo = Column(Text)
    fecha_inicio = Column(Date)
    fecha_fin = Column(Date)
    estado = Column(
        SAEnum("Planificado", "Activo", "Completado", name="sprint_estado_enum"),
        default="Planificado",
    )
    codigo_empresa = Column(Integer, ForeignKey("empresa.codigo_empresa", ondelete="CASCADE"), nullable=False)

    empresa = relationship("Empresa", back_populates="sprints")
    tareas = relationship("Tarea", back_populates="sprint")
