from bson import ObjectId

class BusinessOwnerDAO:
    """
    DAO para manejar usuarios de tipo BusinessOwner en la colección 'usuarios'.
    """
    def __init__(self, db):
        """
        :param db: Objeto de la base de datos (por ejemplo, db = client['turismo_db']).
        """
        self.collection = db.usuarios  # Ajusta si tu colección se llama distinto

    def find_by_id(self, user_id):
        """
        Busca un BusinessOwner por su _id (ObjectId en Mongo).
        Retorna el documento si existe, o None si no.
        """
        return self.collection.find_one({
            "_id": ObjectId(user_id),
            "type": "BusinessOwner"
        })

    def find_by_email(self, email):
        """
        Busca un BusinessOwner por su email.
        Retorna el documento si existe, o None si no.
        """
        return self.collection.find_one({
            "email": email,
            "type": "BusinessOwner"
        })

    def create_business_owner(self, name, email, password):
        """
        Crea un nuevo BusinessOwner en la colección 'usuarios'.
        Retorna el _id generado.
        """
        new_doc = {
            "name": name,
            "email": email,
            "pass": password,   # Ajusta según tu manejo de contraseñas
            "type": "BusinessOwner",
            "blocked": False,
            "properties": []
        }
        result = self.collection.insert_one(new_doc)
        return result.inserted_id

    def update_business_owner(self, user_id, update_fields):
        """
        Actualiza un BusinessOwner existente.
        :param user_id: string o ObjectId del usuario.
        :param update_fields: dict con los campos a actualizar, p. ej. {"name": "NuevoNombre"}.
        Retorna True si se actualizó algo, False si no se encontró.
        """
        filtro = {
            "_id": ObjectId(user_id),
            "type": "BusinessOwner"
        }
        update = {"$set": update_fields}
        result = self.collection.update_one(filtro, update)
        return (result.modified_count > 0)

    def delete_business_owner(self, user_id):
        """
        Elimina un BusinessOwner por su _id.
        Retorna True si se eliminó, False si no existía.
        """
        filtro = {
            "_id": ObjectId(user_id),
            "type": "BusinessOwner"
        }
        result = self.collection.delete_one(filtro)
        return (result.deleted_count > 0)

    # =============================
    # Métodos para manejar 'properties'
    # =============================
    def add_property(self, user_id, property_name):
        """
        Añade una propiedad (string) al array 'properties' de un BusinessOwner.
        """
        filtro = {
            "_id": ObjectId(user_id),
            "type": "BusinessOwner"
        }
        update = {"$push": {"properties": property_name}}
        result = self.collection.update_one(filtro, update)
        return (result.modified_count > 0)

    def remove_property(self, user_id, property_name):
        """
        Elimina una propiedad (string) del array 'properties' de un BusinessOwner.
        """
        filtro = {
            "_id": ObjectId(user_id),
            "type": "BusinessOwner"
        }
        update = {"$pull": {"properties": property_name}}
        result = self.collection.update_one(filtro, update)
        return (result.modified_count > 0)
