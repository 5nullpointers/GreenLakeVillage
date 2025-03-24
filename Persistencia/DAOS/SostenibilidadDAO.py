from Persistencia.AgenteBD import MongoDBAgent

class SostenibilidadDAO:
    COLLECTION = "datos_sostenibilidad"
    global mongoDBAgent
    mongoDBAgent = MongoDBAgent()

    @staticmethod
    def obtener_Consumo():
        pipeline = [
            {"$group": {"_id": None, "total_consumo": {"$sum": "$consumo_energia_kwh"}}}
        ]
        result = list(mongoDBAgent.db[SostenibilidadDAO.COLLECTION].aggregate(pipeline))
        if result:
            return result[0].get("total_consumo", 0)
        return 0
