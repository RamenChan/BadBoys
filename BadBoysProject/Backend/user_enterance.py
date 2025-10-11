from db_connection import client
from datetime import datetime
from sezarV2 import to_hash
from logger import log_error

def user_Add(username, password, salt=None, email=None):
    try:    
        cipher_text, salt = to_hash(password)
        db = client["BadBoys"]
        db["users"].insert_one({
            "username": username,
            "email": email,
            "password_hash": cipher_text,
            "salt": salt,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_login": None,
            "is_active": True,
            "is_verified": False,
            "role": "user",
            "failed_login_attempts": 0,
            "lock_until": None,
            "password_reset_token": None,
            "password_reset_expires": None,
            "auth_provider": "local",
            "profile": {},
            "avatar_url": None,
            "phone": None
        })

        return 1
        
    except Exception as e:
        log_error(str(e), function_name="user_Add")
        return 0


def user_exists(username, password):
    try:
        db = client["BadBoys"]
        user = db["users"].find_one({"username": username})
        
        if not user:
            return 0

        salt_bytes = bytes.fromhex(user.get('salt'))

        cipher_text, _ = to_hash(password, salt_bytes)

        if cipher_text == user.get('password_hash'):
            return 1
        else:
            return 0
        
    except Exception as e:
        log_error(str(e), function_name="user_exists")
        return -1        


