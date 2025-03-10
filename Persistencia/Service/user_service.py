from dao.user_dao import UserDAO
from models.user import User

class UserService:
    def __init__(self, user_dao: UserDAO):
        self.user_dao = user_dao

    def register_user(self, name: str, email: str, password: str, user_type: str):
        """
        Crea un nuevo usuario con la lógica que necesites (validaciones, etc.).
        """
        # Podrías validar si existe un email duplicado, etc.
        # Ejemplo simple:
        new_user = User(name=name, email=email, password=password, user_type=user_type)
        user_id = self.user_dao.create(new_user)
        return user_id

    def login(self, email: str, password: str) -> User:
        """
        Retorna el usuario si el login es correcto. None si es inválido.
        """
        # Podrías buscar un user por email, comparar password, etc.
        # Aquí, el DAO no tiene un "find_by_email", podrías implementarlo:
        user_doc = self.user_dao.collection.find_one({"email": email})
        if not user_doc:
            return None
        
        user = self.user_dao._document_to_user(user_doc)
        if user.password == password:
            return user
        return None

    def change_tokens(self, user_id: str, tokens_to_add: int):
        """
        Ejemplo de un método de lógica: sumarle 'tokens' a un Tourist.
        """
        user = self.user_dao.find_by_id(user_id)
        if not user:
            return False

        # Checamos que sea un Tourist
        if user.user_type == "tourist":
            user.tokens += tokens_to_add
            return self.user_dao.update(user)
        return False
