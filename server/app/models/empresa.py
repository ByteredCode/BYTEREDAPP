from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Empresa(Base):
    __tablename__ = "empresa"

    # PK autoincremental que actúa como discriminador de tenant: cada fila de cualquier tabla
    # del sistema lleva un codigo_empresa, y el middleware de FastAPI lo inyecta automáticamente
    # en toda consulta para garantizar aislamiento entre compañías.
    codigo_empresa = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(150), nullable=False)
    # Código opcional para integración con herramientas Scrum/gestión externas
    codigo_scrum = Column(String(100))
    # Referencia al usuario admin de DPD (sin FK explícita porque puede apuntar a un usuario externo a la BD)
    usuario_admin_dpd = Column(Integer)
    web = Column(String(255))  # URL externa para el módulo de redirección

    # Relaciones ORM: cada relationship() evita tener que escribir JOINs manuales.
    # SQLAlchemy resuelve automáticamente la FK de la tabla hija, permitiendo
    # navegación bidireccional (ej: empresa.usuarios o usuario.empresa).
    usuarios = relationship("Usuario", back_populates="empresa")
    tareas = relationship("Tarea", back_populates="empresa")
    sprints = relationship("Sprint", back_populates="empresa")
    documentos = relationship("Documento", back_populates="empresa")
    tickets = relationship("Ticket", back_populates="empresa")
    fichajes = relationship("Fichaje", back_populates="empresa")
    # cascade="all, delete-orphan": garantiza que al borrar una empresa se eliminen
    # automáticamente sus servicios/feature flags, evitando datos huérfanos en la BD.
    servicios = relationship("EmpresaServicio", back_populates="empresa", cascade="all, delete-orphan")
