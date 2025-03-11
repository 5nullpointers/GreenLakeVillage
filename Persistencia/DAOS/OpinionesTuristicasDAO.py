from Persistencia.AgenteBD import MongoDBAgent

class OpinionesTuristicasDAO:
    COLLECTION = "opiniones_turisticas"
    global mongoDBAgent
    mongoDBAgent = MongoDBAgent()

    @staticmethod
    def insertar_dato(dato):
        return mongoDBAgent.insert_one(OpinionesTuristicasDAO.COLLECTION, dato)

    @staticmethod
    def insertar_varios(datos):
        return mongoDBAgent.insert_many(OpinionesTuristicasDAO.COLLECTION, datos)

    @staticmethod
    def obtener_dato(filtro):
        return mongoDBAgent.find_one(OpinionesTuristicasDAO.COLLECTION, filtro)

    @staticmethod
    def obtener_todos():
        return mongoDBAgent.find(OpinionesTuristicasDAO.COLLECTION)

    @staticmethod
    def actualizar_dato(filtro, nuevo_valor):
        return mongoDBAgent.update_one(OpinionesTuristicasDAO.COLLECTION, filtro, nuevo_valor)

    @staticmethod
    def borrar_dato(filtro):
        return mongoDBAgent.delete_one(OpinionesTuristicasDAO.COLLECTION, filtro)
