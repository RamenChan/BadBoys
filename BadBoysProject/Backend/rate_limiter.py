from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import Config
from system_utilities import system_handshake, ResultCode
import logging


def get_identifier():
    from flask import session, request
    
    username = session.get('username')
    if username:
        return f"user:{username}"
    
    return f"ip:{get_remote_address()}"


def rate_limit_exceeded_handler(e):
    from flask import jsonify
    
    response_data = system_handshake(
        ResultCode.ERROR,
        message="Çok fazla istek gönderdiniz. Lütfen biraz bekleyip tekrar deneyin.",
        data={
            "retry_after": e.description,
            "limit": str(e.limit)
        }
    )
    
    return jsonify({"result": response_data}), 429


limiter = Limiter(
    key_func=get_identifier,
    default_limits=[Config.RATELIMIT_DEFAULT] if Config.RATELIMIT_ENABLED else [],
    storage_uri=Config.RATELIMIT_STORAGE_URL if Config.RATELIMIT_ENABLED else None,
    strategy="fixed-window", 
    headers_enabled=Config.RATELIMIT_HEADERS_ENABLED,
    swallow_errors=Config.RATELIMIT_SWALLOW_ERRORS,
    on_breach=None
)


def init_limiter(app):
    if not Config.RATELIMIT_ENABLED:
        logging.warning("Rate limiting devre dışı!")
        return
    
    try:
        limiter.init_app(app)
        
        app.errorhandler(429)(rate_limit_exceeded_handler)
        
        logging.info(f"Rate limiter başlatıldı: {Config.RATELIMIT_STORAGE_URL}")
        logging.info(f"Default limit: {Config.RATELIMIT_DEFAULT}")
        
    except Exception as e:
        logging.error(f"Rate limiter başlatılamadı: {str(e)}")
        if not Config.RATELIMIT_SWALLOW_ERRORS:
            raise

def login_limit():
    return limiter.limit(Config.RATELIMIT_LOGIN)


def register_limit():
    return limiter.limit(Config.RATELIMIT_REGISTER)


def api_limit():
    return limiter.limit(Config.RATELIMIT_API)


def csrf_limit():
    return limiter.limit(Config.RATELIMIT_CSRF)


def custom_limit(limit_string):
    return limiter.limit(limit_string)


def exempt_from_limit():
    return limiter.exempt