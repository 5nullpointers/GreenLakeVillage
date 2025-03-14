# models/admin.py
from .user import User

class Admin(User):
    def __init__(self,
                 user_id=None,
                 name="",
                 email="",
                 password="",
                 permissions=None):
        super().__init__(user_id, name, email, password, user_type="admin")
        self.permissions = permissions if permissions else {}
