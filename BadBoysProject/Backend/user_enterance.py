from db_connection import client
from datetime import datetime
from sezarV2 import to_hash
from system_utilities import log_error, system_handshake
from core import email_validator, password_validator


def user_add(username, password, salt=None, email=None):
    try:

        db = client["BadBoys"]
        user = db["users"]
        
        cipher_text, salt = to_hash(password)
        
        user.insert_one({
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
        return system_handshake(1, 'Kayıt Başarıyla Gerçekleşti')
        
    except Exception as e:
        log_error(str(e), function_name="user_Add")
        return system_handshake(-99)


def user_add_check(username, password, password_again, email=None):
    try:

        if len(username) < 10:
            return system_handshake(0, 'Kullanıcı Adı En Az 10 karakterden oluşmalıdır.')

        if password != password_again:
            return system_handshake(0, 'Girilen Şifreler Eşleşmiyor.')

        if password_validator(password)==0:
            return system_handshake(0, 'Girilen Şifre şifreleme standartlarına uygun değildir.')

        if email != '' and email_validator(email)==0:
            return system_handshake(0, 'Geçersiz Email girildi.')
        
        db = client["BadBoys"]
        user = db["users"]

        if user.find_one({"username": username}):
                return system_handshake(0, 'Kullanıcı adı daha önceden alınmıştır.')

        return user_add(username, password, email=email)


    except Exception as e:
        log_error(str(e), function_name="user_Add")
        return system_handshake(-99, 'deneme')



def user_exists(username, password):
    try:
        db = client["BadBoys"]
        user = db["users"].find_one({"username": username})
        
        if not user:
            return system_handshake(0, 'Kullanıcı Adı veya Şifre yanlış')

        salt_bytes = bytes.fromhex(user.get('salt'))

        cipher_text, _ = to_hash(password, salt_bytes)

        if cipher_text == user.get('password_hash'):
            return system_handshake(1, 'Kullanıcı Girişi Başarılı')
        else:
            return system_handshake(0, 'Kullanıcı Adı veya Şifre yanlış')
        
    except Exception as e:
        log_error(str(e), function_name="user_exists")
        return system_handshake(-99)       


