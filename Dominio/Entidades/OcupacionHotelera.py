from dataclasses import dataclass
from datetime import date

@dataclass
class OcupacionHotelera:
    hotel_nombre: str
    fecha: date
    tasa_ocupacion: int
    reservas_confirmadas: int
    cancelaciones: int
    precio_promedio_noche: float