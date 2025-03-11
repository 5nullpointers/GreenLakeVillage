from dataclasses import dataclass
from typing import Optional
from datetime import date

@dataclass
class OpinionesTuristicas:
    fecha: date
    tipo_servicio: str
    nombre_servicio: str
    puntuacion: int
    comentario: str
    idioma: Optional[str] = None