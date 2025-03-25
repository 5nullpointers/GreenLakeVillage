from dataclasses import dataclass
from typing import List

@dataclass
class User:
    id: int
    name: str
    email: str
    password: str
    preferencias: List[str]

    def register(self) -> None:
        """Simula el registro de un usuario"""
        print(f"Usuario {self.name} registrado con éxito.")

    def login(self) -> None:
        """Simula el inicio de sesión de un usuario"""
        print(f"Usuario {self.email} ha iniciado sesión.")

    def logout(self) -> None:
        """Simula el cierre de sesión de un usuario"""
        print(f"Usuario {self.email} ha cerrado sesión.")
