class User:
    def __init__(self, 
                 user_id=None, 
                 name="", 
                 email="", 
                 password="", 
                 user_type=""):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.password = password
        self.user_type = user_type  # Ej: "tourist", "businessOwner", "admin"

    def __repr__(self):
        return f"<User {self.name} ({self.user_type})>"
