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
    
    # Metodo para obtener las puntuaciones de los restaurantes
    @staticmethod
    def obtener_agregados_restaurante():
        pipeline = [
            {
                "$match": {
                    "nombre_servicio": {
                        "$in": [
                            "Fábrica Miralles & Asociados S.C.P Restaurante",
                            "Comercial Bru y asociados S.L.L. Restaurante",
                            "Transportes Bou S.L. Restaurante",
                            "Banco Mendez S.Com. Restaurante",
                            "Grupo Pascual S.Com. Restaurante",
                            "Familia Barrera S.Com. Restaurante",
                            "Mir & Asociados S.L. Restaurante",
                            "Suministros Pujol y asociados S.A.T. Restaurante",
                            "Eric Landa Chaparro S.A.U Restaurante",
                            "Minería TVGI S.L.N.E Restaurante",
                            "Grupo Antón S.L. Restaurante",
                            "Grupo Rivas S.A.T. Restaurante",
                            "Alimentación GDF S.Coop. Restaurante",
                            "Suministros BL S.Coop. Restaurante",
                            "Tecnologías Española S.Coop. Restaurante",
                            "Finanzas Coronado y asociados S.L. Restaurante",
                            "Industrias EGVE S.Coop. Restaurante",
                            "Instalaciones Española S.L.L. Restaurante",
                            "Sola y asociados S.Com. Restaurante"
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
