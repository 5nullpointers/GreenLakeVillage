from Persistencia.AgenteBD import MongoDBAgent

class SostenibilidadDAO:
    COLLECTION = "datos_sostenibilidad"
    global mongoDBAgent
    mongoDBAgent = MongoDBAgent()

    @staticmethod
    def insertar_dato(dato):
        return mongoDBAgent.insert_one(SostenibilidadDAO.COLLECTION, dato)

    @staticmethod
    def insertar_varios(datos):
        return mongoDBAgent.insert_many(SostenibilidadDAO.COLLECTION, datos)

    @staticmethod
    def obtener_dato(filtro):
        return mongoDBAgent.find_one(SostenibilidadDAO.COLLECTION, filtro)

    @staticmethod
    def obtener_todos():
        return mongoDBAgent.find(SostenibilidadDAO.COLLECTION)

    @staticmethod
    def actualizar_dato(filtro, nuevo_valor):
        return mongoDBAgent.update_one(SostenibilidadDAO.COLLECTION, filtro, nuevo_valor)

    @staticmethod
    def borrar_dato(filtro):
        return mongoDBAgent.delete_one(SostenibilidadDAO.COLLECTION, filtro)