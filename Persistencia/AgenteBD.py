from dotenv import load_dotenv
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

class MongoDBAgent:
    def __init__(self):
        """
        Inicializa el agente de MongoDB.
        :param uri: URI de conexión de MongoDB Atlas.
        :param db_name: Nombre de la base de datos.
        """
        load_dotenv()
        password = os.getenv("BBDD_PASSWD")
        self.uri = f"mongodb+srv://GreenLakeDBUser:{password}@greenlakedb.6rrmk.mongodb.net/?retryWrites=true&w=majority&appName=GreenLakeDB"
        self.db_name = "turismo_db"
        self.client = None
        self.db = None
        self.connect()

    def connect(self):
        """Establece la conexión con la base de datos."""
        try:
            self.client = MongoClient(self.uri)
            self.db = self.client[self.db_name]
            # print("✅ Conexión a MongoDB establecida correctamente")
        except ConnectionFailure as e:
            print(f"❌ Error al conectar con MongoDB: {e}")

    def insert_one(self, collection: str, document: dict):
        """Inserta un documento en una colección."""
        return self.db[collection].insert_one(document).inserted_id

    def insert_many(self, collection: str, documents: list):
        """Inserta múltiples documentos en una colección."""
        return self.db[collection].insert_many(documents).inserted_ids

    def find_one(self, collection: str, query: dict):
        """Busca un documento en una colección."""
        return self.db[collection].find_one(query)

    def find(self, collection: str, query: dict = {}):
        """Busca múltiples documentos en una colección."""
        return list(self.db[collection].find(query))

    def update_one(self, collection, filtro, update_doc):
        """Actualiza un documento en una colección."""
        return self.db[collection].update_one(filtro, update_doc)

    def delete_one(self, collection: str, query: dict):
        """Elimina un documento de una colección."""
        return self.db[collection].delete_one(query)

    def close_connection(self):
        """Cierra la conexión con MongoDB."""
        if self.client:
            self.client.close()
            print("🔒 Conexión cerrada")
