from Persistencia.AgenteBD import MongoDBAgent

class RutasTuristicasDAO:
    COLLECTION = "rutas_turisticas"
    global mongoDBAgent
    mongoDBAgent = MongoDBAgent()

    @staticmethod
    def insertar_dato(dato):
        return mongoDBAgent.insert_one(RutasTuristicasDAO.COLLECTION, dato)

    @staticmethod
    def insertar_varios(datos):
        return mongoDBAgent.insert_many(RutasTuristicasDAO.COLLECTION, datos)

    @staticmethod
    def obtener_dato(filtro):
        return mongoDBAgent.find_one(RutasTuristicasDAO.COLLECTION, filtro)

    @staticmethod
    def obtener_todos():
        return mongoDBAgent.find(RutasTuristicasDAO.COLLECTION)

    @staticmethod
    def actualizar_dato(filtro, nuevo_valor):
        return mongoDBAgent.update_one(RutasTuristicasDAO.COLLECTION, filtro, nuevo_valor)

    @staticmethod
    def borrar_dato(filtro):
        return mongoDBAgent.delete_one(RutasTuristicasDAO.COLLECTION, filtro)