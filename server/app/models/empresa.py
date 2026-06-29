from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Empresa(Base):
    __tablename__ = "empresa"

    # Modelo central del multi-tenant: todas las tablas referencian codigo_empresa
    codigo_empresa = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(150), nullable=False)
    codigo_scrum = Column(String(100))
    usuario_admin_dpd = Column(Integer)
    web = Column(String(255))  # URL externa para el modulo de redireccion

    # Relaciones con todos los modulos del sistema
    usuarios = relationship("Usuario", back_populates="empresa")
    tareas = relationship("Tarea", back_populates="empresa")
    sprints = relationship("Sprint", back_populates="empresa")
    documentos = relationship("Documento", back_populates="empresa")
    tickets = relationship("Ticket", back_populates="empresa")
    fichajes = relationship("Fichaje", back_populates="empresa")
    # cascade="all, delete-orphan": al borrar empresa se borran sus servicios
    servicios = relationship("EmpresaServicio", back_populates="empresa", cascade="all, delete-orphan")
