@echo off

:: Crear el entorno virtual myenv con los paquetes del sistema
python -m venv --system-site-packages myenv

:: Activar el entorno virtual
call myenv\Scripts\activate

:: Instalar las dependencias desde requirements.txt
pip install -r requirements.txt

:: Iniciar la aplicación
python Dominio\prueba1.py