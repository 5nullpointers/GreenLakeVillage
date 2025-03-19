from dataclasses import dataclass
from typing import List

@dataclass
class RutasTuristicas:
    ruta_nombre: str
    tipo_ruta: str
    longitud_km: float
    duracion_hr: float
    popularidad: float
    origen: List[float]           # [lat, lng]
    punto_intermedio: List[List[float]]  # Lista de puntos [[lat, lng], [lat, lng], ...]
    destino: List[float]          # [lat, lng]
