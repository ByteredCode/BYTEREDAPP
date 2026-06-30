from sqlalchemy import Column, ForeignKey, Integer

from app.core.database import Base


class DocumentoPermiso(Base):
    __tablename__ = "documento_permisos"

    # Tabla pivote para la relacion muchos-a-muchos entre documentos y usuarios.
    # Cada fila representa un permiso explicito de lectura: un par (documento, usuario).
    # Sin esta tabla, controlar acceso por roles no bastaria cuando algunos documentos
    # requieren visibilidad restringida incluso dentro del mismo departamento/empresa.
    id_documento = Column(Integer, ForeignKey("documentos.id_documento", ondelete="CASCADE"), primary_key=True)
    codigo_usuario = Column(Integer, ForeignKey("usuario.codigo_usuario", ondelete="CASCADE"), primary_key=True)
