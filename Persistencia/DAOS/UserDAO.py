from Persistencia.AgenteBD import MongoDBAgent

class UserDAO:
    COLLECTION = "usuarios"
    global mongoDBAgent
    mongoDBAgent = MongoDBAgent()

    @staticmethod
    def insertar_dato(dato):
        return mongoDBAgent.insert_one(UserDAO.COLLECTION, dato)

    @staticmethod
    def insertar_varios(datos):
        return mongoDBAgent.insert_many(UserDAO.COLLECTION, datos)

    @staticmethod
    def obtener_dato(filtro):
        return mongoDBAgent.find_one(UserDAO.COLLECTION, filtro)

    @staticmethod
    def obtener_todos():
        return mongoDBAgent.find(UserDAO.COLLECTION)

    @staticmethod
    def actualizar_dato(filtro, nuevo_valor):
        # Usar pipeline de actualización para aplicar el $set
        return mongoDBAgent.update_one(UserDAO.COLLECTION, filtro, [ { "$set": nuevo_valor } ])

    @staticmethod
    def borrar_dato(filtro):
        return mongoDBAgent.delete_one(UserDAO.COLLECTION, filtro)