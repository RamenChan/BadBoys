# config.py
import os
from dotenv import load_dotenv
from typing import Optional
import secrets



env = os.getenv('FLASK_ENV')

if env == 'live':
    load_dotenv('.env.live')
elif env == 'test':
    load_dotenv('.env.test')
else:
    load_dotenv('.env.dev')

class BaseConfig:
    """Base configuration - ortak ayarlar"""
    
    # ============================================
    # APPLICATION
    # ============================================
    APP_NAME = "BadBoys"
    VERSION = "1.0.0"
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY tanımlanmalı!")
    
    # ============================================
    # MONGODB
    # ============================================
    MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
    MONGO_PORT = int(os.getenv('MONGO_PORT', 27017))
    MONGO_USER = os.getenv('MONGO_USER')
    MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')
    MONGO_DB = os.getenv('MONGO_DB', 'BadBoys')
    MONGO_AUTH_SOURCE = os.getenv('MONGO_AUTH_SOURCE')
    
    # MongoDB TLS
    MONGO_TLS = os.getenv('MONGO_TLS', 'false').lower() == 'true'
    MONGO_TLS_CA_FILE = os.getenv('MONGO_TLS_CA_FILE')
    MONGO_TLS_CERT_FILE = os.getenv('MONGO_TLS_CERT_FILE')
    MONGO_TLS_ALLOW_INVALID = os.getenv('MONGO_TLS_ALLOW_INVALID', 'false').lower() == 'true'
    
    # MongoDB Connection Pool
    MONGO_MAX_POOL_SIZE = int(os.getenv('MONGO_MAX_POOL_SIZE', 50))
    MONGO_MIN_POOL_SIZE = int(os.getenv('MONGO_MIN_POOL_SIZE', 10))
    MONGO_SERVER_SELECTION_TIMEOUT = int(os.getenv('MONGO_SERVER_SELECTION_TIMEOUT', 5000))
    MONGO_CONNECT_TIMEOUT = int(os.getenv('MONGO_CONNECT_TIMEOUT', 10000))
    MONGO_SOCKET_TIMEOUT = int(os.getenv('MONGO_SOCKET_TIMEOUT', 20000))
    
    # ============================================
    # ENCRYPTION
    # ============================================
    """MASTER_3DES_KEY = os.getenv('MASTER_3DES_KEY')
    if not MASTER_3DES_KEY:
        raise ValueError("MASTER_3DES_KEY tanımlanmalı!")
    """
    # Key Rotation
    KEY_ROTATION_INTERVAL = int(os.getenv('KEY_ROTATION_INTERVAL', 600)) 
    
    # Password Hashing
    PBKDF2_ITERATIONS = int(os.getenv('PBKDF2_ITERATIONS', 100_000))
    PBKDF2_ALGORITHM = os.getenv('PBKDF2_ALGORITHM', 'sha256')
    
    # Sezar Algorithm
    SEZAR_PASSES = int(os.getenv('SEZAR_PASSES', 2))
    
    # ============================================
    # SECURITY
    # ============================================
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS').split(',')
        
    # Session
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'false').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = os.getenv('SESSION_COOKIE_HTTPONLY', 'true').lower() == 'true'
    SESSION_COOKIE_SAMESITE = os.getenv('SESSION_COOKIE_SAMESITE', 'None')
    SESSION_TYPE = os.getenv('SESSION_TYPE', 'filesystem')
    SESSION_FILE_DIR = os.getenv('SESSION_FILE_DIR', './flask_session')
    PERMANENT_SESSION_LIFETIME = int(os.getenv('PERMANENT_SESSION_LIFETIME', 3600))

    #CSRF
    CSRF_ENABLED = os.getenv('CSRF_ENABLED', 'true').lower() == 'true'
    CSRF_TIME_LIMIT = int(os.getenv('CSRF_TIME_LIMIT', 3600))
    WTF_CSRF_TIME_LIMIT = int(os.getenv('CSRF_TIME_LIMIT', 3600)) 
    
    # CSRF COOKIE SETTINGS
    CSRF_COOKIE_SECURE = os.getenv('CSRF_COOKIE_SECURE', 'false').lower() == 'true'
    CSRF_COOKIE_HTTPONLY = os.getenv('CSRF_COOKIE_HTTPONLY', 'false').lower() == 'true'
    CSRF_COOKIE_SAMESITE = os.getenv('CSRF_COOKIE_SAMESITE', 'Strict')

    # SOCKET.IO
    SOCKETIO_CORS_ALLOWED_ORIGINS = os.getenv('SOCKETIO_CORS_ALLOWED_ORIGINS', 'http://localhost:5173').split(',')
    SOCKETIO_ASYNC_MODE = os.getenv('SOCKETIO_ASYNC_MODE', 'eventlet')

    
    # Brute Force Protection
    USER_WARN_LOCK = int(os.getenv('USER_WARN_LOCK', 3))
    USER_TEMP_LOCK_TIME = int(os.getenv('USER_TEMP_LOCK_TIME', 900)) 
    USER_HARD_LOCK = int(os.getenv('USER_HARD_LOCK', 6))
    
    IP_WARN_LOCK = int(os.getenv('IP_WARN_LOCK', 10))
    IP_TEMP_LOCK_TIME = int(os.getenv('IP_TEMP_LOCK_TIME', 1800))  # 30 dakika
    IP_HARD_LOCK = int(os.getenv('IP_HARD_LOCK', 30))
    IP_HARD_LOCK_TIME = int(os.getenv('IP_HARD_LOCK_TIME', 86400))  # 24 saat

    # Password Policy
    PASSWORD_MIN_LENGTH = int(os.getenv('PASSWORD_MIN_LENGTH'))
    PASSWORD_MAX_LENGTH = int(os.getenv('PASSWORD_MAX_LENGTH'))
    USERNAME_MIN_LENGTH = int(os.getenv('USERNAME_MIN_LENGTH'))
    
    # ============================================
    # DATA FETCHING
    # ============================================
    DATA_FETCH_INTERVAL = int(os.getenv('DATA_FETCH_INTERVAL', 60)) 
    HACKER_NEWS_API_URL = os.getenv('HACKER_NEWS_API_URL', 'https://hacker-news.firebaseio.com/v0')
    HACKER_NEWS_HTML_URL = os.getenv('HACKER_NEWS_HTML_URL', 'https://news.ycombinator.com/news')
    MAX_STORIES_FETCH = int(os.getenv('MAX_STORIES_FETCH', 20))
   
    # ============================================
    # BRUTEFORCE HANDLER
    # ============================================
    USER_WARN_LOCK = int(os.getenv('USER_WARN_LOCK'))
    USER_TEMP_LOCK_TIME = int(os.getenv('USER_TEMP_LOCK_TIME'))
    USER_HARD_LOCK = int(os.getenv('USER_HARD_LOCK'))

    IP_WARN_LOCK = int(os.getenv('IP_WARN_LOCK'))
    IP_TEMP_LOCK_TIME = int(os.getenv('IP_TEMP_LOCK_TIME')) 
    IP_HARD_LOCK = int(os.getenv('IP_HARD_LOCK'))
    IP_HARD_LOCK_TIME = int(os.getenv('IP_HARD_LOCK_TIME')) 

    # ============================================
    # LOGGING
    # ============================================
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/badboys.log')
    LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', 10485760))  # 10MB
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 10))
    
    # ============================================
    # REDIS
    # ============================================
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
    REDIS_SOCKET_TIMEOUT = int(os.getenv('REDIS_SOCKET_TIMEOUT', 5))
    REDIS_SOCKET_CONNECT_TIMEOUT = int(os.getenv('REDIS_SOCKET_CONNECT_TIMEOUT', 5))
    REDIS_MAX_CONNECTIONS = int(os.getenv('REDIS_MAX_CONNECTIONS', 50))
    @classmethod
    def get_redis_url(cls):
        """Redis connection URL oluştur"""
        if cls.REDIS_PASSWORD:
            return f"redis://:{cls.REDIS_PASSWORD}@{cls.REDIS_HOST}:{cls.REDIS_PORT}/{cls.REDIS_DB}"
        return f"redis://{cls.REDIS_HOST}:{cls.REDIS_PORT}/{cls.REDIS_DB}"
    
    # ============================================
    # RATE LIMITING
    # ============================================
    RATELIMIT_ENABLED = os.getenv('RATELIMIT_ENABLED', 'true').lower() == 'true'
    RATELIMIT_STORAGE_URL = os.getenv('RATELIMIT_STORAGE_URL')
    
    # Default limits
    RATELIMIT_DEFAULT = os.getenv('RATELIMIT_DEFAULT', '200/hour;50/minute')
    
    # Endpoint specific limits
    RATELIMIT_LOGIN = os.getenv('RATELIMIT_LOGIN', '5/minute;20/hour')
    RATELIMIT_REGISTER = os.getenv('RATELIMIT_REGISTER', '3/minute;10/hour')
    RATELIMIT_API = os.getenv('RATELIMIT_API', '100/minute;1000/hour')
    RATELIMIT_CSRF = os.getenv('RATELIMIT_CSRF', '10/minute')
    
    # Headers
    RATELIMIT_HEADERS_ENABLED = os.getenv('RATELIMIT_HEADERS_ENABLED', 'true').lower() == 'true'
    RATELIMIT_SWALLOW_ERRORS = os.getenv('RATELIMIT_SWALLOW_ERRORS', 'true').lower() == 'true'

    # ============================================
    # JWT CONFIGURATION
    # ============================================
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 900)) 
    JWT_REFRESH_TOKEN_EXPIRES = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', 604800)) 
    
    # Token location
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_COOKIE_SECURE = os.getenv('JWT_COOKIE_SECURE', 'false').lower() == 'true'
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_COOKIE_SAMESITE = 'Lax'
    
    # Blacklist için Redis
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']



    # ============================================
    # VALIDATION
    # ============================================
    @classmethod
    def validate(cls):
        """Configuration validation"""
        errors = []
        
        # Required fields
        required = [
            'SECRET_KEY',
            'MONGO_USER',
            'MONGO_PASSWORD',
        ]
        
        for field in required:
            if not getattr(cls, field, None):
                errors.append(f"{field} tanımlanmalı!")
        
        # MongoDB TLS validation
        if cls.MONGO_TLS and not cls.MONGO_TLS_CA_FILE and not cls.MONGO_TLS_ALLOW_INVALID:
            errors.append("MONGO_TLS açık ama CA sertifikası yok!")
        
        # Password policy validation
        if cls.PASSWORD_MIN_LENGTH > cls.PASSWORD_MAX_LENGTH:
            errors.append("PASSWORD_MIN_LENGTH > PASSWORD_MAX_LENGTH olamaz!")
        
        #Redis validation
        if cls.RATELIMIT_ENABLED and not cls.RATELIMIT_STORAGE_URL:
            cls.RATELIMIT_STORAGE_URL = cls.get_redis_url()
        
        if errors:
            raise ValueError(f"Configuration hataları:\n" + "\n".join(f"- {e}" for e in errors))
        
        return True


class DevConfig(BaseConfig):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    RELOADER=False
    
    # Development için daha detaylı loglar
    LOG_LEVEL = 'DEBUG'
    
    # CORS - tüm origin'lere izin (sadece development)
    CORS_ORIGINS = ['*']
    
    # Session - HTTP cookie (HTTPS olmadan çalışır)
    SESSION_COOKIE_SECURE = False
    
    # MongoDB - TLS opsiyonel
    MONGO_TLS_ALLOW_INVALID = True

    # Rate Limiting
    RATELIMIT_DEFAULT = '500/hour;100/minute'
    RATELIMIT_LOGIN = '10/minute;50/hour'
    RATELIMIT_REGISTER = '5/minute;20/hour'



class LiveConfig(BaseConfig):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    RELOADER=False

    
    # Production için sadece önemli loglar
    LOG_LEVEL = 'WARNING'
    
    # CORS - sadece belirli origin'ler
    # CORS_ORIGINS env'den gelecek
    
    # Session - Güvenli cookie
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'None'    

    # MongoDB - TLS zorunlu
    MONGO_TLS_ALLOW_INVALID = False
    
    USER_WARN_LOCK = 3
    IP_WARN_LOCK = 5

    # Rate Limiting
    RATELIMIT_DEFAULT = '100/hour;30/minute'
    RATELIMIT_LOGIN = '3/minute;10/hour'
    RATELIMIT_REGISTER = '2/minute;5/hour'
    
    # Production'da hataları yut
    RATELIMIT_SWALLOW_ERRORS = True


class TestConfig(BaseConfig):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    RELOADER=False

    
    # Test database
    MONGO_DB = 'BadBoys_Test'
    
    # CORS - sadece belirli origin'ler
    # CORS_ORIGINS env'den gelecek

    # Hızlı testler için düşük timeout
    MONGO_SERVER_SELECTION_TIMEOUT = 1000
    MONGO_CONNECT_TIMEOUT = 2000
    
    # Hızlı key rotation (test için)
    KEY_ROTATION_INTERVAL = 10
    
    # Hızlı brute force testi
    USER_WARN_LOCK = 2
    USER_TEMP_LOCK_TIME = 5


    # Rate Limiting
    RATELIMIT_DEFAULT = '10000/hour;1000/minute'


# ============================================
# CONFIGURATION SELECTOR
# ============================================
config_map = {
    'dev': DevConfig,
    'live': LiveConfig,
    'test': TestConfig,
}


current_env = os.getenv('FLASK_ENV', 'dev')
Config = config_map.get(current_env, DevConfig)


ACTIVE_ENV_FILE = (
    '.env.production' if current_env == 'production' else
    '.env.test' if current_env == 'test' else
    '.env.dev'
)


try:
    Config.validate()
    print(f"Configuration loaded: {current_env}")
except ValueError as e:
    print(f"Configuration error: {e}")
    raise