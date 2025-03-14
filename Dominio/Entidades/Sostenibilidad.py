from dataclasses import dataclass
from datetime import date

@dataclass
class Sostenibilidad:
    hotel_nombre: str
    consumo_energia_kwh: int
    residuos_generados_kg: int
    porcentaje_reciclaje: float
    uso_agua_m3: int
    fecha: date