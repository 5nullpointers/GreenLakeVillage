from dataclasses import dataclass

@dataclass
class RutasTuristicas:
    ruta_nombre: str
    tipo_ruta: str
    longitud_km: float
    duracion_hr: float
    popularidad: float