from sqlalchemy import Column, Date, Enum as SAEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class Tarea(Base):
    __tablename__ = "tareas"

    codigo_tarea = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text)
    # Prioridad con valores fijos conocidos; se usa Enum SQL en vez de una tabla separada
    # porque el conjunto de valores no cambia y simplifica las consultas
    prioridad = Column(
        SAEnum("Baja", "Media", "Alta", "Critica", name="prioridad_enum"),
        default="Media",
    )
    # Las 4 columnas del tablero Kanban clásico. Se guardan como Enum SQL para evitar
    # errores tipográficos y permitir ordenación semántica en el frontend
    columna = Column(
        SAEnum("Todo", "Haciendose", "En revision", "Done", name="columna_enum"),
        default="Todo",
    )
    orden = Column(Integer, default=0)  # Posición dentro de la columna (drag & drop); default 0 evita valores NULL
    fecha_limite = Column(Date)
    # ondelete="SET NULL": si se elimina el usuario asignado o el sprint, la tarea no se pierde,
    # simplemente queda desasignada para que un admin pueda reasignarla después
    asignacion = Column(Integer, ForeignKey("usuario.codigo_usuario", ondelete="SET NULL"))
    codigo_sprint = Column(Integer, ForeignKey("sprints.codigo_sprint", ondelete="SET NULL"))
    # Tenant FK con CASCADE: al borrar la empresa se borran todas sus tareas
    codigo_empresa = Column(Integer, ForeignKey("empresa.codigo_empresa", ondelete="CASCADE"), nullable=False)

    # relationship() permite acceder desde una tarea a su empresa o sprint sin escribir JOINs explícitos
    empresa = relationship("Empresa", back_populates="tareas")
    sprint = relationship("Sprint", back_populates="tareas")
