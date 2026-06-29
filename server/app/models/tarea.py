from sqlalchemy import Column, Date, Enum as SAEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class Tarea(Base):
    __tablename__ = "tareas"

    codigo_tarea = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text)
    prioridad = Column(
        SAEnum("Baja", "Media", "Alta", "Critica", name="prioridad_enum"),
        default="Media",
    )
    # columna representa el estado en el tablero Kanban (4 columnas clasicas)
    columna = Column(
        SAEnum("Todo", "Haciendose", "En revision", "Done", name="columna_enum"),
        default="Todo",
    )
    orden = Column(Integer, default=0)  # Posicion dentro de la columna (drag & drop)
    fecha_limite = Column(Date)
    # SET NULL: si se borra el usuario o sprint, la tarea permanece sin asignar
    asignacion = Column(Integer, ForeignKey("usuario.codigo_usuario", ondelete="SET NULL"))
    codigo_sprint = Column(Integer, ForeignKey("sprints.codigo_sprint", ondelete="SET NULL"))
    codigo_empresa = Column(Integer, ForeignKey("empresa.codigo_empresa", ondelete="CASCADE"), nullable=False)

    empresa = relationship("Empresa", back_populates="tareas")
    sprint = relationship("Sprint", back_populates="tareas")
