from system_utilities import system_handshake, ResultCode
from db_connection import client
from core import now_ts


class bruteforce_protector:
    
    USER_WARN_LOCK = 3
    USER_TEMP_LOCK_TIME = 15*60  # 15 dk
    USER_HARD_LOCK = 6 

    IP_WARN_LOCK = 10
    IP_TEMP_LOCK_TIME = 30*60    # 30 dk
    IP_HARD_LOCK = 30
    IP_HARD_LOCK_TIME = 24*60*60 # 24 saat

    def __init__(self, db_name='BadBoys'):

        self.client = client
        self.db = self.client[db_name]
        self.users_collection = self.db["users"]
        self.ip_collection = self.db["ips"]
        
    def bruteforce_check(self, username = None, ip=None):
        try:
            now = now_ts()
            return_message = []

            if username:
                user = self.users_collection.find_one({'username': username})
                if user:

                    lock_until = user.get('lock_until')
                    
                    if user.get('is_active') is False:
                        return_message.append('Hesabınız askıya alınmıştır. Lütfen şifremi unuttum bölümden yeni şifre alınız.')
                    
                    elif lock_until and lock_until > now:
                        return_message.append('Hesabınız geçici olarak kilitlidir. Lütfen daha sonra tekrar deneyiniz.')
                    
                    elif user.get('failed_login_attempts', 0) >= self.USER_HARD_LOCK:
                        self.users_collection.update_one({'username': username},
                                                        {'$set' :{'is_active': False}})
                        return_message.append("Çok fazla hatalı giriş yapıldı. Hesabınız bir süreliğine askıya alınmıştır. Lütfen yeni şifre alınız.")
            
            if ip:
                ip_doc = self.ip_collection.find_one({'ip':ip})
                if ip_doc:
                    lock_until = ip_doc.get("lock_until")

                    if ip_doc.get("is_active") is False:
                        return_message.append(" Bu IP adresi bir süreliğine engellenmiştir." )


                    elif lock_until and lock_until > now:
                        return_message.append("Bu IP adresinden çok fazla hatalı istek geldi. Lütfen daha sonra tekrar deneyiniz.")

            if return_message:
                return system_handshake(ResultCode.INFO, return_message)
            return system_handshake(ResultCode.SUCCESS)
        
        except Exception as e:
            return system_handshake(ResultCode.ERROR, error_message=str(e), function_name="bruteforce_handler/bruteforce_check")

    def logon_fail(self, username=None, ip=None):

        try:

            now = now_ts()
            return_message = []


            if username:
                user = self.users_collection.find_one({'username': username})
                if user:
                    self.users_collection.update_one({"username": username}, 
                                                    {"$inc": {"failed_login_attempts": 1},
                                                    "$set": {"last_attempt": now}})
                    
                    user = self.users_collection.find_one({"username": username})
                    fails = user.get("failed_login_attempts", 0)

                    if fails == self.USER_WARN_LOCK:
                        lock_until = now + self.USER_TEMP_LOCK_TIME
                        self.users_collection.update_one({'username': username},
                                                        {'$set':{'lock_until': lock_until}})
                        return_message.append("Çok fazla hatalı giriş yapıldı. Hesabınız bir süreliğine askıya alınmıştır. Lütfen yeni şifre alınız.")
                    
                    elif fails >= self.USER_HARD_LOCK:
                        self.users_collection.update_one({'username': username},
                                                        {'$set' :{'is_active': False}})
                        return_message.append("Çok fazla hatalı giriş yapıldı. Hesabınız süresiz askıya alınmıştır. Lütfen yeni şifre alınız.")
                
            if ip:
                self.ip_collection.update_one({'ip':ip},
                                            {"$inc": {"failed_login_attempts": 1}, 
                                            "$set": {"last_attempt": now, "ip": ip}}
                                            , upsert=True)
                
                ip_doc = self.ip_collection.find_one({'ip':ip})
                ip_fails = ip_doc.get('failed_login_attempts', 0)

                if ip_fails == self.IP_WARN_LOCK:
                    lock_until = now + self.IP_TEMP_LOCK_TIME
                    self.ip_collection.update_one({"ip": ip}, {"$set": {"lock_until": lock_until}})
                    return_message.append("Bu IP adresi geçici olarak (30 dk) engellenmiştir.")
                
                elif ip_fails >= self.IP_HARD_LOCK:
                    lock_until = now + self.IP_HARD_LOCK_TIME
                    self.ip_collection.update_one({"ip":ip}, {"$set": {"lock_until": lock_until, "is_active": False}})
                    return_message.append("Bu IP adresi geçici olarak (24 saat) engellenmiştir.")
                
            if return_message:
                return system_handshake(ResultCode.INFO, message= 'Giriş Başarısız.',data=return_message)
            return system_handshake(ResultCode.INFO, 'Kullanıcı Adı veya Şifre Yanlış')
        
        except Exception as e:
            return system_handshake(ResultCode.ERROR, error_message=str(e), function_name="bruteforce_handler/logon_fail")


    def logon_success(self, username, ip):
        try:
            now = now_ts()

            if username:
                user = self.users_collection.find_one({'username':username})
                if user:
                    self.users_collection.update_one({"username": username}, 
                                                    {"$set": {"failed_login_attempts": 0, 
                                                            "lock_until": None, 
                                                            "last_attempt": now, 
                                                            "is_active": True,
                                                            "last_login": now}})
                    
            if ip:
                self.ip_collection.update_one({"ip":ip}, 
                                            {"$set": {"failed_login_attempts": 0, 
                                                        "lock_until": None, 
                                                        "last_attempt": now, 
                                                        "ip": ip, 
                                                        "is_active": True}}
                                                        , upsert=True)
            
            return system_handshake(ResultCode.SUCCESS, 'Giriş Başarılı')
        
        except Exception as e:
                return system_handshake(ResultCode.ERROR, error_message=str(e), function_name="bruteforce_handler/logon_success")
            