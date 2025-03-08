import pymongo
from tabulate import tabulate

# Conectar a MongoDB (local)
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["turismo_db"]

def listar_colecciones():
    colecciones = db.list_collection_names()
    print("\nColecciones disponibles:\n")
    print(tabulate([[col] for col in colecciones], headers=["Colección"]))

def mostrar_documentos(coleccion, limite=5):
    print(f"\nPrimeros {limite} documentos de la colección '{coleccion}':\n")
    documentos = list(db[coleccion].find().limit(limite))
    if documentos:
        print(tabulate(documentos, headers="keys", tablefmt="grid"))
    else:
        print("No hay documentos en esta colección.")

def contar_documentos():
    print("\nConteo de documentos por colección:\n")
    data = [[col, db[col].count_documents({})] for col in db.list_collection_names()]
    print(tabulate(data, headers=["Colección", "Cantidad de Documentos"], tablefmt="grid"))

def filtrar_opiniones(calificacion_minima=4.5):
    print(f"\nOpiniones con calificación superior a {calificacion_minima}:\n")
    query = {"calificacion": {"$gt": calificacion_minima}}
    documentos = list(db["opiniones_turisticas"].find(query))
    print(tabulate(documentos, headers="keys", tablefmt="grid"))

def buscar_rutas_por_ciudad(ciudad):
    print(f"\nRutas turísticas en {ciudad}:\n")
    query = {"ciudad": ciudad}
    documentos = list(db["rutas_turisticas"].find(query))
    print(tabulate(documentos, headers="keys", tablefmt="grid"))

def hoteles_mayor_ocupacion(limite=5):
    print("\nHoteles con mayor ocupación:\n")
    documentos = list(db["ocupacion_hotelera"].find().sort("ocupacion", -1).limit(limite))
    print(tabulate(documentos, headers="keys", tablefmt="grid"))

def promedio_ocupacion_por_ciudad():
    print("\nPromedio de ocupación por ciudad:\n")
    pipeline = [
        {"$group": {"_id": "$ciudad", "ocupacion_media": {"$avg": "$ocupacion"}}}
    ]
    documentos = list(db["ocupacion_hotelera"].aggregate(pipeline))
    print(tabulate(documentos, headers="keys", tablefmt="grid"))

def transporte_mas_utilizado():
    print("\nUso de transporte más frecuente:\n")
    pipeline = [
        {"$group": {"_id": "$tipo_transporte", "total_uso": {"$sum": 1}}},
        {"$sort": {"total_uso": -1}}
    ]
    documentos = list(db["uso_transporte"].aggregate(pipeline))
    print(tabulate(documentos, headers="keys", tablefmt="grid"))

# Ejecutar consultas con mejor visualización
listar_colecciones()
mostrar_documentos("ocupacion_hotelera")
contar_documentos()
filtrar_opiniones()
buscar_rutas_por_ciudad("Madrid")
hoteles_mayor_ocupacion()
promedio_ocupacion_por_ciudad()
transporte_mas_utilizado()
