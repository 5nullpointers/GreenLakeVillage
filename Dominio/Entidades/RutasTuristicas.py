from dataclasses import dataclass
from typing import List

@dataclass
class RutasTuristicas:
    ruta_nombre: str
    tipo_ruta: str
    longitud_km: float
    duracion_hr: float
    popularidad: float
    coordenadas: List[float]