from sqlalchemy import Column, ForeignKey, Integer

from app.core.database import Base


class DocumentoPermiso(Base):
    __tablename__ = "documento_permisos"

    # Clave compuesta: relacion muchos-a-muchos entre documentos y usuarios
    # Un usuario puede ver un documento solo si tiene permiso explicito (o es admin)
    id_documento = Column(Integer, ForeignKey("documentos.id_documento", ondelete="CASCADE"), primary_key=True)
    codigo_usuario = Column(Integer, ForeignKey("usuario.codigo_usuario", ondelete="CASCADE"), primary_key=True)
