from Persistencia.AgenteBD import MongoDBAgent

class UsoTransporteDAO:
    COLLECTION = "uso_transporte"
    global mongoDBAgent
    mongoDBAgent = MongoDBAgent()

    @staticmethod
    def insertar_dato(dato):
        return mongoDBAgent.insert_one(UsoTransporteDAO.COLLECTION, dato)

    @staticmethod
    def insertar_varios(datos):
        return mongoDBAgent.insert_many(UsoTransporteDAO.COLLECTION, datos)

    @staticmethod
    def obtener_dato(filtro):
        return mongoDBAgent.find_one(UsoTransporteDAO.COLLECTION, filtro)

    @staticmethod
    def obtener_todos():
        return mongoDBAgent.find(UsoTransporteDAO.COLLECTION)

    @staticmethod
    def actualizar_dato(filtro, nuevo_valor):
        return mongoDBAgent.update_one(UsoTransporteDAO.COLLECTION, filtro, nuevo_valor)

    @staticmethod
    def borrar_dato(filtro):
        return mongoDBAgent.delete_one(UsoTransporteDAO.COLLECTION, filtro)
