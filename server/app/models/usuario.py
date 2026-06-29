from sqlalchemy import Column, Enum as SAEnum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Usuario(Base):
    __tablename__ = "usuario"

    codigo_usuario = Column(Integer, primary_key=True, autoincrement=True)
    # Email unico a nivel de BD para evitar duplicados
    correo = Column(String(150), nullable=False, unique=True)
    # Almacenamos el hash bcrypt, no la contrasena en texto plano
    contrasena = Column(String(255), nullable=False)
    nombre = Column(String(150), nullable=False)
    # Tres roles: admin_total (superadmin), admin_empresa (gestor), usuario (empleado)
    rol = Column(SAEnum("admin_total", "admin_empresa", "usuario", name="rol_enum"), nullable=False, default="usuario")
    # FK a empresa con CASCADE: al borrar empresa se borran sus usuarios
    codigo_empresa = Column(Integer, ForeignKey("empresa.codigo_empresa", ondelete="CASCADE"), nullable=False)

    empresa = relationship("Empresa", back_populates="usuarios")
