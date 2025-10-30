from datetime import datetime, timedelta
from system_utilities import system_handshake, ResultCode
from db_connection import client

class bruteforce_protector:
    
    USER_WARN_LOCK = 3
    USER_TEMP_LOCK_TIME = timedelta(minutes=15)
    USER_HARD_LOCK = 6 

    IP_WARN_LOCK = 10
    IP_TEMP_LOCK_TIME = timedelta(minutes=30)
    IP_HARD_LOCK = 30
    IP_HARD_LOCK_TIME = timedelta(hours=24)

    def __init__(self, db_name='BadBoys'):

        self.client = client
        self.db = self.client[db_name]
        self.users_collection = self.db["users"]
        self.ip_collection = self.db["ips"]
    
    def date_now(self):
        return datetime.now()
        
    def bruteforce_check(self, username = None, ip=None):
        now = self.date_now()

        if username:
            user = self.users_collection.find_one({'username': username})
            if user:
                if user.get('is_active') is False:
                    return system_handshake(ResultCode.INFO, 'Hesabınız askıya alınmıştır. Lütfen şifremi unuttum bölümden yeni şifre alınız.')
                
                lock_until = user.get('lock_until')
                if lock_until and lock_until > now:
                    return system_handshake(ResultCode.INFO, 'Hesabınız geçici olarak kilitlidir. Lütfen daha sonra tekrar deneyiniz.')
                
                if user.get('failed_login_attempts', 0) >= self.USER_HARD_LOCK:
                    self.users_collection.update_one({'username': username},
                                                     {'$set' :{'is_active': False}})
                    return system_handshake(ResultCode.INFO, "Çok fazla hatalı giriş yapıldı. Hesabınız bir süreliğine askıya alınmıştır. Lütfen yeni şifre alınız.")
        
        if ip:
            ip_doc = self.ip_collection.find_one({'ip':ip})
            if ip_doc:
                if ip_doc.get("is_active") is False:
                    return system_handshake(ResultCode.INFO, "Bu IP adresi engellenmiştir.")


                lock_until = ip_doc.get("lock_until")
                if lock_until and lock_until > now:
                    return system_handshake(ResultCode.INFO, "Bu IP adresinden çok fazla hatalı istek geldi. Lütfen daha sonra tekrar deneyiniz.")


        return system_handshake(ResultCode.SUCCESS)
    

    def logon_fail(self, username=None, ip=None):

        now = self.date_now()

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
                    return system_handshake(ResultCode.INFO, "Çok fazla hatalı giriş yapıldı. Hesabınız bir süreliğine askıya alınmıştır. Lütfen yeni şifre alınız.")
                
                if fails >= self.USER_HARD_LOCK:
                    self.users_collection.update_one({'username': username},
                                                     {'$set' :{'is_active': False}})
                    return system_handshake(ResultCode.INFO, "Çok fazla hatalı giriş yapıldı. Hesabınız süresiz askıya alınmıştır. Lütfen yeni şifre alınız.")
                
        if ip:
            self.ip_collection.update_one({'ip':ip},
                                        {"$inc": {"failed_login_attempts": 1}, 
                                        "$set": {"last_attempt": now, "ip": ip, "is_active": True}}
                                        , upsert=True)
            
            ip_doc = self.ip_collection.find_one({'ip':ip})
            ip_fails = ip_doc.get('failed_login_attempts', 0)

            if ip_fails == self.IP_WARN_LOCK +1:
                lock_until = now + self.IP_TEMP_LOCK_TIME
                self.ip_collection.update_one({"ip": ip}, {"$set": {"lock_until": lock_until}})
                return system_handshake(ResultCode.INFO, "Bu IP adresi geçici olarak (30 dk) engellenmiştir.")
            
            if ip_fails >= self.IP_HARD_LOCK:
                lock_until = now + self.IP_HARD_LOCK_TIME
                self.ip_collection.update_one({"ip":ip}, {"$set": {"lock_until": lock_until, "is_active": False}})
                return system_handshake(ResultCode.INFO, "Bu IP adresi geçici olarak (24 saat) engellenmiştir.")
            
        return system_handshake(ResultCode.SUCCESS)
    
    def logon_success(self, username, ip):

        now = self.date_now()

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
        
        return system_handshake(ResultCode.SUCCESS)
            