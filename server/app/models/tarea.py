from sqlalchemy import Column, Enum as SAEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class Tarea(Base):
    __tablename__ = "tareas"

    codigo_tarea = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text)
    asignacion = Column(Integer, ForeignKey("usuario.codigo_usuario", ondelete="SET NULL"))
    columna = Column(
        SAEnum("Todo", "Haciendose", "En revision", "Done", name="columna_enum"),
        default="Todo",
    )
    codigo_empresa = Column(Integer, ForeignKey("empresa.codigo_empresa", ondelete="CASCADE"), nullable=False)

    empresa = relationship("Empresa", back_populates="tareas")
