from db_connection import client
from datetime import datetime
from sezarV2 import to_hash
from system_utilities import system_handshake, ResultCode
from core import email_validator, password_validator
from datetime import datetime, timedelta
import hmac



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
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
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

        password_result = password_validator(password)
        if password_result["code"] != ResultCode.SUCCESS:
            return password_result

        if email != None: 
            if email_validator(email)["code"] == ResultCode.FAIL:
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

        if not username:#aşşağıdaki kontrol ile aynı kontrol değil. hiçbir bilgi girilmediyse db bağlantısı açmadan hata fırlatır.
            return system_handshake(ResultCode.INFO, 'Kullanıcı Adı veya Şifre yanlış')

        db = client["BadBoys"]
        user = db["users"].find_one({"username": username})
        
        if not user:
            return system_handshake(ResultCode.INFO, 'Kullanıcı Adı veya Şifre yanlış')

        if user_state(username)['code'] == ResultCode.INFO:
            return system_handshake(ResultCode.INFO, 'Hesabınız askıya alınmış durumdadır. Lütfen yeni şifre alınız.')

        salt_bytes = bytes.fromhex(user.get('salt'))

        result = to_hash(password, salt_bytes)

        if hmac.compare_digest(result["data"]["cipher_text"], user.get('password_hash')):    
            return logon_success(username)
        else:
            return logon_fail(username)
        
    except Exception as e:  
        return system_handshake(ResultCode.ERROR, error_message=str(e), function_name="user_enterance/user_exists")    
    
def logon_fail(username):
    try:
        db = client["BadBoys"]
        users = db["users"]  

        user = users.find_one({"username": username})
        if not user:
            return system_handshake(ResultCode.INFO, "Kullanıcı bulunamadı")

        attempts = int(user.get('failed_login_attempts', 0))
        lock_until = user.get('lock_until')

        if lock_until and lock_until > datetime.now():
            users.update_one(
                {"_id": user["_id"]},
                {"$set": {"is_active": False}}
            )
            return system_handshake(
                ResultCode.INFO,
                "Çok fazla hatalı giriş yapıldı. Hesabınız süresiz askıya alınmıştır. Lütfen yeni şifre alınız."
            )    
            
        elif 0 <= attempts < 3:
            users.update_one(
                {"_id": user["_id"]},
                {"$inc": {"failed_login_attempts": 1}}
            )
            return system_handshake(ResultCode.INFO, "Kullanıcı Adı veya Şifre yanlış")

        elif attempts == 3:
            users.update_one(
                {"_id": user["_id"]},
                {
                    "$set": {"lock_until": datetime.now() + timedelta(minutes=15)},
                    "$inc": {"failed_login_attempts": 1}
                }
            )
            return system_handshake(ResultCode.INFO, "Çok fazla hatalı giriş yapıldı. Hesabınız 15 dk askıya alınmıştır.")

    except Exception as e:
        return system_handshake(ResultCode.ERROR, error_message=str(e), function_name="user_enterance/wrong_entrance")



def logon_success(username):
    
    try:
        db = client["BadBoys"]
        users = db["users"]  

        user = users.find_one({"username": username})
        users.update_one(
            {"_id": user["_id"]},
            {"$set": {"failed_login_attempts": 0, "lock_until": None}}
        )

        return system_handshake(ResultCode.SUCCESS, "Kullanıcı Girişi Başarılı")

    except Exception as e:
        return system_handshake(
            ResultCode.ERROR,
            error_message=str(e),
            function_name="user_enterance/logon_success"
        )




def user_state(username):
    try:
        
        db = client["BadBoys"]
        users = db["users"]  

        user = users.find_one({"username": username})

        if user['is_active'] == True:
            return system_handshake(ResultCode.SUCCESS)
        elif user['is_active'] == False:
            return system_handshake(ResultCode.INFO, 'Hesabınız askıya alınmış durumdadır. Lütfen E-Posta doğrulaması yapınız.')    
        
    except Exception as e:
        return system_handshake(
            ResultCode.ERROR,
            error_message=str(e),
            function_name="user_enterance/user_state"
        )