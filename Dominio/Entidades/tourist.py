# models/tourist.py
from .user import User

class Tourist(User):
    def __init__(self,
                 user_id=None,
                 name="",
                 email="",
                 password="",
                 tokens=0,
                 achievements=None,
                 favourite_routes=None):
        super().__init__(user_id, name, email, password, user_type="tourist")
        self.tokens = tokens
        self.achievements = achievements if achievements else []
        self.favourite_routes = favourite_routes if favourite_routes else []
