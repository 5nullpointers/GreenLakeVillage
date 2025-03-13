from Persistencia.AgenteBD import MongoDBAgent

class UserDAO:
    COLLECTION = "usuarios"
    global mongoDBAgent
    mongoDBAgent = MongoDBAgent()

    def __init__(self, config=None):
        # Para futuras inicializaciones o uso de configuración
        self.config = config

    @staticmethod
    def find_by_email(email: str):
        return mongoDBAgent.find_one(UserDAO.COLLECTION, {"email": email})

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
        return mongoDBAgent.update_one(UserDAO.COLLECTION, filtro, nuevo_valor)

    @staticmethod
    def borrar_dato(filtro):
        return mongoDBAgent.delete_one(UserDAO.COLLECTION, filtro)