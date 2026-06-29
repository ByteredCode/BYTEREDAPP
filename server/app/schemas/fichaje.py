from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class FichajeResponse(BaseModel):
    id_fichaje: int
    codigo_empresa: int
    codigo_usuario: int
    hora_entrada: datetime
    hora_salida: Optional[datetime] = None

    model_config = {"from_attributes": True}


class FichajeResumenResponse(BaseModel):
    horas_hoy: float
    horas_semana: float
    horas_mes: float
    total_fichajes: int
