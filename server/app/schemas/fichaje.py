from datetime import datetime
from typing import Optional

from pydantic import BaseModel

# ── Schemas del módulo de fichaje ─────────────────────────────────────
# Curiosamente, aquí no hay schemas de creación (Create). ¿Por qué?
# Porque un fichaje no se "crea" con datos del formulario, sino que se
# registra automáticamente cuando el usuario pulsa "Entrar/Salir". El
# endpoint solo recibe un POST vacío (el usuario se identifica por JWT).
# Esto simplifica el frontend y evita que se pueda falsear la hora.


class FichajeResponse(BaseModel):
    id_fichaje: int
    codigo_empresa: int
    codigo_usuario: int
    hora_entrada: datetime
    # hora_salida es None hasta que el usuario vuelve a pulsar "Salir".
    # Esto nos permite saber qué fichajes siguen abiertos (sin cerrar).
    hora_salida: Optional[datetime] = None

    model_config = {"from_attributes": True}


class FichajeResumenResponse(BaseModel):
    # Segundo nivel de detalle: en lugar de devolver todos los fichajes
    # del día, devolvemos métricas agregadas (horas totales) que son
    # más útiles para el dashboard del usuario que la lista cruda.
    horas_hoy: float
    horas_semana: float
    horas_mes: float
    total_fichajes: int
