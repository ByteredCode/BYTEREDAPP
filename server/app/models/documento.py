from sqlalchemy import Column, Date, Enum as SAEnum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Documento(Base):
    __tablename__ = "documentos"

    id_documento = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(255), nullable=False)
    codigo_empresa = Column(Integer, ForeignKey("empresa.codigo_empresa", ondelete="CASCADE"), nullable=False)
    usuario_subio = Column(Integer, ForeignKey("usuario.codigo_usuario"), nullable=False)
    fecha = Column(Date, nullable=False)
    ruta_archivo = Column(String(255))
    tipo_documento = Column(SAEnum("DPD", "ISO", name="tipo_doc_enum"))

    empresa = relationship("Empresa", back_populates="documentos")
