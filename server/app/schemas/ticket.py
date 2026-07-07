from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

# ── Schemas del módulo de tickets ─────────────────────────────────────
# Separamos creación, actualización de estado y respuesta para evitar
# que el cliente pueda modificar campos que no le corresponden
# (por ej. un usuario no debería poder cambiar el estado a "resuelto"
#  sin que el admin lo procese).


class TicketCreate(BaseModel):
    nombre_contacto: Optional[str] = None
    correo_contacto: str
    asunto: Optional[str] = None
    nivel_importancia: str = Field(default="Media", pattern=r"^(Baja|Media|Alta|Critica)$")
    mensaje: str
    codigo_empresa: int


class TicketUpdateEstado(BaseModel):
    # Este schema es deliberadamente pequeño: solo permitimos cambiar
    # el estado y añadir una respuesta. El resto de campos (asunto,
    # mensaje, etc.) son inmutables una vez creados por razones de
    # auditoría (trazabilidad del ticket).
    estado: str = Field(pattern=r"^(Pendiente|Leido|Respondido|Cerrado)$")
    respuesta: Optional[str] = None


class TicketResponse(BaseModel):
    id_reporte: int
    codigo_usuario: Optional[int] = None
    nombre_contacto: Optional[str] = None
    correo_contacto: Optional[str] = None
    asunto: Optional[str] = None
    nivel_importancia: str
    mensaje: str
    codigo_empresa: int
    estado: str
    fecha_reporte: Optional[datetime] = None
    respuesta: Optional[str] = None
    fecha_respuesta: Optional[datetime] = None

    model_config = {"from_attributes": True}
