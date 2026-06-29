from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class FichajeResponse(BaseModel):
    id_fichaje: int
    codigo_empresa: int
    codigo_usuario: int
    hora_entrada: datetime
    hora_salida: Optional[datetime] = None  # None = fichaje actualmente abierto

    model_config = {"from_attributes": True}
