from dataclasses import dataclass
from datetime import date

@dataclass
class UsoTransporte:
    fecha: date
    tipo_transporte: str
    num_usuarios: int
    tiempo_viaje_promedio_min: int
    ruta_popular: str