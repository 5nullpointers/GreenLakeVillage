from pymongo import MongoClient
from bson import ObjectId

from models.user import User
from models.tourist import Tourist
from models.business_owner import BusinessOwner
from models.admin import Admin

class UserDAO:
    def __init__(self, mongo_client: MongoClient, db_name: str = "miBase"):
        # db_name puede ser un string con el nombre de tu DB en Mongo
        self.db = mongo_client[db_name]
        self.collection = self.db["users"]  # la colección se llama "users"

    def create(self, user: User) -> str:
        """
        Inserta un usuario en la colección y devuelve el id (string).
        """
        user_dict = self._user_to_document(user)
        result = self.collection.insert_one(user_dict)
        return str(result.inserted_id)

    def find_by_id(self, user_id: str) -> User:
        """
        Busca un documento por _id y lo convierte a la entidad adecuada.
        """
        doc = self.collection.find_one({"_id": ObjectId(user_id)})
        if doc:
            return self._document_to_user(doc)
        return None

    def update(self, user: User) -> bool:
        """
        Actualiza un usuario. Devuelve True si se ha modificado algo, False si no.
        """
        if not user.user_id:
            return False  # no hay ID para actualizar
        user_dict = self._user_to_document(user)
        # Evitar duplicar _id en user_dict
        user_dict["_id"] = ObjectId(user.user_id)
        result = self.collection.replace_one({"_id": ObjectId(user.user_id)}, user_dict)
        return result.modified_count > 0

    def delete(self, user_id: str) -> bool:
        """
        Elimina un usuario por _id.
        """
        result = self.collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0

    def _user_to_document(self, user: User) -> dict:
        """
        Convierte la entidad User (o subclases) a un dict para MongoDB.
        """
        doc = {
            "name": user.name,
            "email": user.email,
            "password": user.password,
            "type": user.user_type
        }
        # Si tiene user_id, lo convertimos a ObjectId
        if user.user_id:
            doc["_id"] = ObjectId(user.user_id)

        # Dependiendo del tipo, añadimos campos específicos
        if user.user_type == "tourist" and isinstance(user, Tourist):
            doc["tokens"] = user.tokens
            doc["achievements"] = user.achievements
            doc["favourite_routes"] = user.favourite_routes

        elif user.user_type == "businessOwner" and isinstance(user, BusinessOwner):
            doc["locations"] = user.locations

        elif user.user_type == "admin" and isinstance(user, Admin):
            doc["permissions"] = user.permissions

        return doc

    def _document_to_user(self, doc: dict) -> User:
        """
        Convierte un doc de Mongo en la subclase adecuada (Tourist, Admin, etc.).
        """
        _id = str(doc["_id"])
        user_type = doc.get("type", "")

        if user_type == "tourist":
            return Tourist(
                user_id=_id,
                name=doc.get("name"),
                email=doc.get("email"),
                password=doc.get("password"),
                tokens=doc.get("tokens", 0),
                achievements=doc.get("achievements", []),
                favourite_routes=doc.get("favourite_routes", [])
            )
        elif user_type == "businessOwner":
            return BusinessOwner(
                user_id=_id,
                name=doc.get("name"),
                email=doc.get("email"),
                password=doc.get("password"),
                locations=doc.get("locations", [])
            )
        elif user_type == "admin":
            return Admin(
                user_id=_id,
                name=doc.get("name"),
                email=doc.get("email"),
                password=doc.get("password"),
                permissions=doc.get("permissions", {})
            )
        else:
            # Por defecto, un user genérico
            return User(
                user_id=_id,
                name=doc.get("name"),
                email=doc.get("email"),
                password=doc.get("password"),
                user_type=user_type
            )
