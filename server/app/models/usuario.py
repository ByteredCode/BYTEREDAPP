from sqlalchemy import Column, Enum as SAEnum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Usuario(Base):
    __tablename__ = "usuario"

    # PK autoincremental: cada usuario recibe un ID único. El aislamiento multi-tenant se aplica
    # mediante el middleware que filtra todas las consultas por codigo_empresa, no por el PK.
    codigo_usuario = Column(Integer, primary_key=True, autoincrement=True)
    # Email único en toda la BD (no solo por empresa) porque el login usa correo + contraseña
    # a nivel global; el tenant se asigna tras la autenticación.
    correo = Column(String(150), nullable=False, unique=True)
    # Almacenamos el hash bcrypt, no la contraseña en texto plano
    contrasena = Column(String(255), nullable=False)
    nombre = Column(String(150), nullable=False)
    # Roles definidos como Enum SQL porque el sistema tiene tres niveles jerárquicos fijos:
    #   admin_total   → superadmin global con acceso a todas las empresas
    #   admin_empresa → gestor que administra usuarios y módulos de su compañía
    #   usuario       → empleado base con permisos limitados a su rol funcional
    rol = Column(SAEnum("admin_total", "admin_empresa", "usuario", name="rol_enum"), nullable=False, default="usuario")
    # FK con CASCADE: al eliminar una empresa, todos sus usuarios se borran automáticamente.
    # codigo_empresa es el discriminador de tenant que el middleware inyecta en cada consulta.
    codigo_empresa = Column(Integer, ForeignKey("empresa.codigo_empresa", ondelete="CASCADE"), nullable=False)

    # Usamos relationship() en lugar de JOINs manuales para que SQLAlchemy resuelva automáticamente
    # la FK al acceder a usuario.empresa, cargando el objeto Empresa relacionado bajo demanda.
    empresa = relationship("Empresa", back_populates="usuarios")
