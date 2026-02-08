# jwt_manager.py
from flask_jwt_extended import JWTManager
from redis_connection import RedisConnection
from system_utilities import system_handshake, ResultCode
from datetime import timedelta

jwt = JWTManager()

def init_jwt(app):
    """JWT Manager'ı başlat"""
    jwt.init_app(app)
    
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        """Token blacklist kontrolü (Redis)"""
        jti = jwt_payload['jti']
        try:
            redis_client = RedisConnection.get_client()
            token_in_redis = redis_client.get(f"blacklist:{jti}")
            return token_in_redis is not None
        except Exception as e:
            print(f"Redis blacklist check error: {e}")
            return False
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        """Token süresi dolduğunda"""
        return system_handshake(
            ResultCode.ERROR,
            message="Token süresi doldu. Lütfen yeniden giriş yapın."
        ), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        """Geçersiz token"""
        return system_handshake(
            ResultCode.ERROR,
            message="Geçersiz token. Lütfen yeniden giriş yapın."
        ), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        """Token eksik"""
        return system_handshake(
            ResultCode.ERROR,
            message="Yetkisiz erişim. Lütfen giriş yapın."
        ), 401
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        """Token iptal edilmiş"""
        return system_handshake(
            ResultCode.ERROR,
            message="Token iptal edildi. Lütfen yeniden giriş yapın."
        ), 401


def add_token_to_blacklist(jti, expires_delta):
    """Token'ı blacklist'e ekle (logout için)"""
    try:
        redis_client = RedisConnection.get_client()
        redis_client.setex(
            f"blacklist:{jti}",
            expires_delta,
            "true"
        )
        return True
    except Exception as e:
        print(f"Blacklist ekleme hatası: {e}")
        return False