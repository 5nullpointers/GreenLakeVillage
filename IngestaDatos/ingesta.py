import pandas as pd
import pymongo
from pymongo import MongoClient

# Conectar a MongoDB (local)
client = MongoClient("mongodb://localhost:27017/")
db = client["turismo_db"]  # Nombre de la base de datos

# Definir archivos y colecciones
files_collections = {
    "data/datos_sostenibilidad.csv": "datos_sostenibilidad",
    "data/ocupacion_hotelera.csv": "ocupacion_hotelera",
    "data/opiniones_turisticas.csv": "opiniones_turisticas",
    "data/rutas_turisticas.csv": "rutas_turisticas",
    "data/uso_transporte.csv": "uso_transporte",
}

# Iterar sobre los archivos y cargarlos en MongoDB
for file_path, collection_name in files_collections.items():
    try:
        # Leer el archivo CSV
        df = pd.read_csv(file_path)
        
        # Convertir a diccionario
        data = df.to_dict(orient="records")
        
        # Insertar en la colección
        collection = db[collection_name]
        if data:
            collection.insert_many(data)
            print(f"Insertados {len(data)} registros en la colección {collection_name}")
        else:
            print(f"El archivo {file_path} está vacío o no tiene datos válidos.")
    except Exception as e:
        print(f"Error al procesar {file_path}: {e}")

print("Proceso de ingesta completado.")
