from Persistencia.AgenteBD import MongoDBAgent

class HotelesDAO:
    COLLECTION = "hoteles"
    global mongoDBAgent
    mongoDBAgent = MongoDBAgent()

    @staticmethod
    def obtener_precios():
        # Se usa el método find del driver de MongoDB con la proyección
        return list(mongoDBAgent.db[HotelesDAO.COLLECTION].find({}, {"nombre": 1, "precio": 1}))
