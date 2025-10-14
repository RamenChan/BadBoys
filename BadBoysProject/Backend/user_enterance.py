from db_connection import client
from datetime import datetime
from sezarV2 import to_hash
from system_utilities import system_handshake, ResultCode
from core import email_validator, password_validator


def user_add(username, password, salt=None, email=None):
    try:

        db = client["BadBoys"]
        user = db["users"]
        
        result = to_hash(password)
        
        user.insert_one({
            "username": username,
            "email": email,
            "password_hash": result["data"]["cipher_text"],
            "salt": result["data"]["salt"],
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
        return system_handshake(ResultCode.SUCCESS, 'Kayıt Başarıyla Gerçekleşti')
        
    except Exception as e:
        return system_handshake(ResultCode.ERROR, error_message=str(e), function_name= "user_enterance/user_Add")


def user_add_check(username, password, password_again, email=None):
    try:

        if len(username) < 10:
            return system_handshake(ResultCode.INFO, 'Kullanıcı Adı En Az 10 karakterden oluşmalıdır.')

        if password != password_again:
            return system_handshake(ResultCode.INFO, 'Girilen Şifreler Eşleşmiyor.')

        if password_validator(password)["code"] == ResultCode.FAIL:
            return system_handshake(ResultCode.INFO, 'Girilen Şifre şifreleme standartlarına uygun değildir.')

        if email != '' and email_validator(email)["code"] == ResultCode.FAIL:
            return system_handshake(ResultCode.INFO, 'Geçersiz Email girildi.')
        
        db = client["BadBoys"]
        user = db["users"]

        if user.find_one({"username": username}):
                return system_handshake(ResultCode.INFO, 'Kullanıcı adı daha önceden alınmıştır.')

        return user_add(username, password, email=email)


    except Exception as e:
        return system_handshake(ResultCode.ERROR, error_message=str(e), function_name="user_enterance/user_add_check")


def user_exists(username, password):
    try:
        db = client["BadBoys"]
        user = db["users"].find_one({"username": username})
        
        if not user:
            return system_handshake(ResultCode.INFO, 'Kullanıcı Adı veya Şifre yanlış')

        salt_bytes = bytes.fromhex(user.get('salt'))

        result = to_hash(password, salt_bytes)

        if result["data"]["cipher_text"] == user.get('password_hash'):
            return system_handshake(ResultCode.SUCCESS, 'Kullanıcı Girişi Başarılı')
        else:
            return system_handshake(ResultCode.INFO, 'Kullanıcı Adı veya Şifre yanlış')
        
    except Exception as e:  
        return system_handshake(ResultCode.ERROR, error_message=str(e), function_name="user_enterance/user_exists")    


