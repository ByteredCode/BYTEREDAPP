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
    # Estado del sprint con Enum fijo porque el ciclo de vida en Scrum es conocido
    # y acotado: Planificado → Activo → Completado (sin estados intermedios)
    estado = Column(
        SAEnum("Planificado", "Activo", "Completado", name="sprint_estado_enum"),
        default="Planificado",
    )
    # FK al tenant con CASCADE: los sprints pertenecen a una empresa y se borran con ella
    codigo_empresa = Column(Integer, ForeignKey("empresa.codigo_empresa", ondelete="CASCADE"), nullable=False)

    # Relaciones ORM para navegación bidireccional: desde un sprint podemos acceder
    # a su empresa o a sus tareas sin necesidad de JOINs explícitos
    empresa = relationship("Empresa", back_populates="sprints")
    tareas = relationship("Tarea", back_populates="sprint")
