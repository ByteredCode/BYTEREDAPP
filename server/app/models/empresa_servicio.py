from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class EmpresaServicio(Base):
    __tablename__ = "empresa_servicios"

    # Feature flags por empresa: en lugar de tener una columna booleana por cada
    # posible modulo (tiene_scrum, tiene_tickets...), usamos una tabla EAV
    # (entity-attribute-value) con filas (empresa, servicio, activo).
    # Esto permite anadir nuevos modulos sin migrar el esquema: solo insertar
    # filas en esta tabla y en company_services (tabla de definicion de modulos).
    codigo_empresa = Column(Integer, ForeignKey("empresa.codigo_empresa", ondelete="CASCADE"), primary_key=True)
    servicio = Column(String(50), primary_key=True)
    activo = Column(Boolean, default=True)

    empresa = relationship("Empresa", back_populates="servicios")
