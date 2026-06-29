from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class EmpresaServicio(Base):
    __tablename__ = "empresa_servicios"

    # Clave compuesta: cada empresa tiene una fila por servicio
    # Esto es mas escalable que tener columnas como tiene_scrum, tiene_tickets...
    codigo_empresa = Column(Integer, ForeignKey("empresa.codigo_empresa", ondelete="CASCADE"), primary_key=True)
    servicio = Column(String(50), primary_key=True)
    activo = Column(Boolean, default=True)

    empresa = relationship("Empresa", back_populates="servicios")
