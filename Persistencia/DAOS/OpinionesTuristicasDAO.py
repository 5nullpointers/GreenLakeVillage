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

    @staticmethod
    def obtener_opiniones_y_media(hotel_nombre):
        """
        Obtiene todas las opiniones y calcula la media de puntuación para un hotel dado.
        Filtra por el campo 'nombre_servicio', que debe coincidir con el nombre del hotel.
        Las opiniones se ordenan por fecha (más recientes primero).
        Retorna una tupla: (lista_de_opiniones, media_puntuacion)
        """
        filtro = {"nombre_servicio": hotel_nombre}
        # Orden descendente: las opiniones más recientes primero
        opiniones = list(mongoDBAgent.db[OpinionesTuristicasDAO.COLLECTION].find(filtro).sort("fecha", -1))
        if opiniones:
            media = sum(opinion.get("puntuacion", 0) for opinion in opiniones) / len(opiniones)
        else:
            media = None
        return opiniones, media



    # Metodo para obtener las puntuaciones de los hoteles 
    @staticmethod
    def obtener_agregados():
        """
        Ejecuta la agregación para obtener la media de puntuación y el número de opiniones
        para cada hotel (según la lista definida).
        """
        pipeline = [
            {
                "$match": {
                    "nombre_servicio": {
                        "$in": [
                            "Alletra Boutique Hotel", 
                            "Alletra Diamond Grand Hotel", 
                            "Alletra Haven", 
                            "Alletra Resort", 
                            "Apollo Diamond Suites", 
                            "Apollo Executive Beach Resort", 
                            "Aruba Lodge", 
                            "Aruba Luxury Lodge", 
                            "Cray Villas", 
                            "Ezmeral Grand Hotel", 
                            "GreenLake Digital Business Suites", 
                            "GreenLake Platinum Heritage Inn", 
                            "InfoSight Boutique Hotel", 
                            "Pointnext Signature Residences & Suites", 
                            "Primera Grand", 
                            "ProLiant Haven", 
                            "ProLiant Place", 
                            "ProLiant Towers", 
                            "Simplivity Golden Plaza Hotel", 
                            "Synergy Golden Grand Hotel", 
                            "dHCI Executive Boutique Hotel", 
                            "Apollo Resort & Spa", 
                            "Apollo Towers", 
                            "dHCI Platinum Beach Resort"
                        ]
                    }
                }
            },
            {
                "$group": {
                    "_id": "$nombre_servicio",
                    "media_puntuacion": { "$avg": "$puntuacion" },
                    "numero_comentarios": { "$sum": 1 }
                }
            },
            {
                "$sort": { "numero_comentarios": -1 }
            }
        ]
        return list(mongoDBAgent.db[OpinionesTuristicasDAO.COLLECTION].aggregate(pipeline))