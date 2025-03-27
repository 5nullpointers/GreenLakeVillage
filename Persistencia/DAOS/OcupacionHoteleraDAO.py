from Persistencia.AgenteBD import MongoDBAgent

class OcupacionHoteleraDAO:
    COLLECTION = "ocupacion_hotelera"
    global mongoDBAgent
    mongoDBAgent = MongoDBAgent()

    @staticmethod
    def insertar_dato(dato):
        return mongoDBAgent.insert_one(OcupacionHoteleraDAO.COLLECTION, dato)

    @staticmethod
    def insertar_varios(datos):
        return mongoDBAgent.insert_many(OcupacionHoteleraDAO.COLLECTION, datos)

    @staticmethod
    def obtener_dato(filtro):
        return mongoDBAgent.find_one(OcupacionHoteleraDAO.COLLECTION, filtro)

    @staticmethod
    def obtener_todos():
        return mongoDBAgent.find(OcupacionHoteleraDAO.COLLECTION)

    @staticmethod
    def actualizar_dato(filtro, nuevo_valor):
        return mongoDBAgent.update_one(OcupacionHoteleraDAO.COLLECTION, filtro, nuevo_valor)

    @staticmethod
    def borrar_dato(filtro):
        return mongoDBAgent.delete_one(OcupacionHoteleraDAO.COLLECTION, filtro)
    
    @staticmethod
    def UsuariosTotales():
        pipeline = [
            { "$group": { "_id": "$hotel_nombre", "reservas": { "$sum": "$reservas_confirmadas" } } },
            { "$group": { "_id": None, "totalReservas": { "$sum": "$reservas" } } }
        ]
        result = list(mongoDBAgent.db[OcupacionHoteleraDAO.COLLECTION].aggregate(pipeline))
        if result and len(result) > 0:
            return result[0].get('totalReservas', 0)
        return 0
    
    @staticmethod
    def total_reservas_confirmadas():
        pipeline = [
            {"$group": {"_id": None, "totalReservas": {"$sum": "$reservas_confirmadas"}}}
        ]
        result = list(mongoDBAgent.db[OcupacionHoteleraDAO.COLLECTION].aggregate(pipeline))
        if result and len(result) > 0:
            return result[0].get("totalReservas", 0)
        return 0

    @staticmethod
    def total_cancelaciones():
        pipeline = [
            {"$group": {"_id": None, "totalCancelaciones": {"$sum": "$cancelaciones"}}}
        ]
        result = list(mongoDBAgent.db[OcupacionHoteleraDAO.COLLECTION].aggregate(pipeline))
        if result and len(result) > 0:
            return result[0].get("totalCancelaciones", 0)
        return 0

    @staticmethod
    def obtener_por_nombre(nombre_hotel):
        """
        Busca en la colección ocupacion_hotelera el documento cuyo 'hotel_nombre' coincida.
        Retorna el documento o None si no existe.
        """
        filtro = {"hotel_nombre": nombre_hotel}
        return mongoDBAgent.find_one(OcupacionHoteleraDAO.COLLECTION, filtro)
