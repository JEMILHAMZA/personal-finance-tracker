from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId

class User(UserMixin):
    def __init__(self, user_id, username, email, password=None):
        self.id = str(user_id)  # Set the user ID
        self.username = username  # Store the username
        self.email = email  # Store the email
        self.password = password  # Store the password (optional)


    @staticmethod
    def create(username, email, password):
        from app import mongo  # Importing here to avoid circular dependency
        hashed_password = generate_password_hash(password)
        user_id = mongo.db.users.insert_one({
            "username": username,
            "email": email,
            "password": hashed_password
        }).inserted_id
        return str(user_id)

    @staticmethod
    def get(user_id):
        from app import mongo  # Importing here as well
        user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if user_data:
            return User(user_data['_id'], user_data['username'], user_data['email'], user_data['password'])
        return None


    @staticmethod
    def get_by_username_or_email(identifier):
        from app import mongo
        return mongo.db.users.find_one({"$or": [{"username": identifier}, {"email": identifier}]})

    @staticmethod
    def verify_password(stored_password, provided_password):
        return check_password_hash(stored_password, provided_password)
