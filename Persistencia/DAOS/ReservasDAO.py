# Persistencia/DAOS/ReservasDAO.py

from Persistencia.AgenteBD import MongoDBAgent

class ReservasDAO:
    COLLECTION = "reservas"
    global mongoDBAgent
    mongoDBAgent = MongoDBAgent()

    @staticmethod
    def insertar_reserva(reserva_doc):
        """
        Inserta un documento de reserva en la colección 'reservas'.
        """
        return mongoDBAgent.insert_one(ReservasDAO.COLLECTION, reserva_doc)

    @staticmethod
    def obtener_reservas_por_hotel(hotel_id):
        """
        Devuelve un cursor con las reservas del hotel dado.
        """
        filtro = {"hotelId": hotel_id}
        return mongoDBAgent.find(ReservasDAO.COLLECTION, filtro)
