#!/bin/bash

# Crear el entorno virtual myenv con los paquetes del sistema
python3 -m venv --system-site-packages myenv

# Activar el entorno virtual
source myenv/bin/activate

# Instalar las dependencias desde requirements.txt
pip install -r requirements.txt

# Iniciar la aplicación
python3 Dominio/prueba1.py