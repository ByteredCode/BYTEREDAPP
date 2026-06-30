from datetime import date
from typing import Optional

from pydantic import BaseModel

# ── Schemas del módulo de documentos DPD/ISO ─────────────────────────
# Tampoco hay schema de creación aquí: los documentos se suben mediante
# multipart/form-data (archivo + metadatos), no por JSON. FastAPI puede
# recibir los metadatos como form fields sin necesidad de un schema
# Pydantic. El response sí es útil para devolver los datos del archivo
# ya registrado.


class DocumentoResponse(BaseModel):
    id_documento: int
    nombre: str  # Guardamos el nombre original para mostrarlo al usuario
    codigo_empresa: int
    usuario_subio: int
    fecha: date
    tipo_documento: Optional[str] = None  # "DPD" o "ISO" — distingue el módulo legal
    ruta_archivo: Optional[str] = None  # Ruta física en el servidor (no se expone al frontend normalmente)

    model_config = {"from_attributes": True}


class PermisoAgregar(BaseModel):
    # Schema mínimo: solo necesitamos el ID del usuario que obtendrá
    # permiso para ver ese documento. El id_documento se pasa por URL.
    codigo_usuario: int


class PermisoResponse(BaseModel):
    id_documento: int
    codigo_usuario: int

    model_config = {"from_attributes": True}
