from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.core.database import Base


class Fichaje(Base):
    __tablename__ = "fichajes"

    id_fichaje = Column(Integer, primary_key=True, autoincrement=True)
    codigo_empresa = Column(Integer, ForeignKey("empresa.codigo_empresa", ondelete="CASCADE"), nullable=False)
    codigo_usuario = Column(Integer, ForeignKey("usuario.codigo_usuario", ondelete="CASCADE"), nullable=False)
    hora_entrada = Column(DateTime, nullable=False)
    hora_salida = Column(DateTime)  # NULL mientras el usuario esta fichado (sin salir)

    empresa = relationship("Empresa", back_populates="fichajes")
