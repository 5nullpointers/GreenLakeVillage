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
    def obtener_tipo_servicio(nombre_servicio):
        """
        Devuelve el tipo_servicio (Hotel, Restaurante, etc.) de la primera opinión del servicio dado.
        """
        opinion = mongoDBAgent.db[OpinionesTuristicasDAO.COLLECTION].find_one(
            {"nombre_servicio": nombre_servicio},
            {"_id": 0, "tipo_servicio": 1}
        )
        return opinion.get("tipo_servicio", "N/A") if opinion else "N/A"

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
                            # Agregar restaurantes:
                            "Alimentación GDF S.Coop. Restaurante",
                            "Banco Mendez S.Com. Restaurante",
                            "Comercial Bru y asociados S.L.L. Restaurante",
                            "Eric Landa Chaparro S.A.U Restaurante",
                            "Familia Barrera S.Com. Restaurante",
                            "Finanzas Coronado y asociados S.L. Restaurante",
                            "Fábrica Miralles & Asociados S.C.P Restaurante",
                            "Grupo Antón S.L. Restaurante",
                            "Grupo Pascual S.Com. Restaurante",
                            "Grupo Rivas S.A.T. Restaurante",
                            "Industrias EGVE S.Coop. Restaurante",
                            "Instalaciones Española S.L.L. Restaurante",
                            "Minería TVGI S.L.N.E Restaurante",
                            "Mir & Asociados S.L. Restaurante",
                            "Sola y asociados S.Com. Restaurante",
                            "Suministros BL S.Coop. Restaurante",
                            "Suministros Pujol y asociados S.A.T. Restaurante",
                            "Tecnologías Española S.Coop. Restaurante",
                            "Transportes Bou S.L. Restaurante"
                            "Restauración SL S.L.L. Atracción",
                            "Restauración XRI S.Com. Transporte",
                            "Restauración del Sur S.Com. Tour Guiado"
                            # Farmacias
                            # Tiendas
                            # Parque
                            # Atracciones
                            # Museos
                            # Transporte
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
    
    # Obtener el top 3 de hoteles
    @staticmethod
    def obtener_top_hoteles():
        pipeline = [
            { "$match": { "tipo_servicio": "Hotel" } },
            { "$group": {
                "_id": "$nombre_servicio",
                "media_puntuacion": { "$avg": "$puntuacion" },
                "numero_comentarios": { "$sum": 1 }
            }},
            { "$sort": { "media_puntuacion": -1 } },
            { "$limit": 3 }
        ]
        return list(mongoDBAgent.db[OpinionesTuristicasDAO.COLLECTION].aggregate(pipeline))

    # Obtener el top 3 de servicios
    @staticmethod
    def obtener_top_servicios():
        pipeline = [
            { "$match": { "tipo_servicio": "Servicio" } },
            { "$group": {
                "_id": "$nombre_servicio",
                "media_puntuacion": { "$avg": "$puntuacion" },
                "numero_comentarios": { "$sum": 1 }
            }},
            { "$sort": { "media_puntuacion": -1 } },
            { "$limit": 3 }
        ]
        return list(mongoDBAgent.db[OpinionesTuristicasDAO.COLLECTION].aggregate(pipeline))

    # Obtener el top 3 de rutas
    @staticmethod
    def obtener_top_rutas():
        pipeline = [
            { "$match": { "tipo_servicio": "Ruta" } },
            { "$group": {
                "_id": "$nombre_servicio",
                "media_puntuacion": { "$avg": "$puntuacion" },
                "numero_comentarios": { "$sum": 1 }
            }},
            { "$sort": { "media_puntuacion": -1 } },
            { "$limit": 3 }
        ]
        return list(mongoDBAgent.db[OpinionesTuristicasDAO.COLLECTION].aggregate(pipeline))