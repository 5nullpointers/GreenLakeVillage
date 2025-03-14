# models/business_owner.py
from .user import User

class BusinessOwner(User):
    def __init__(self,
                 user_id=None,
                 name="",
                 email="",
                 password="",
                 locations=None):
        super().__init__(user_id, name, email, password, user_type="businessOwner")
        self.locations = locations if locations else []
