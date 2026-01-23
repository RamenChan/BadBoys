import redis
from redis.exceptions import ConnectionError, TimeoutError
from config import Config
from system_utilities import system_handshake, ResultCode


class RedisConnection:
    
    _client = None
    _connection_pool = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            cls._client = cls._create_client()
        return cls._client

    @classmethod
    def _create_client(cls):
        try:
            cls._connection_pool = redis.ConnectionPool(
                host=Config.REDIS_HOST,
                port=Config.REDIS_PORT,
                db=Config.REDIS_DB,
                password=Config.REDIS_PASSWORD if Config.REDIS_PASSWORD else None,
                socket_timeout=Config.REDIS_SOCKET_TIMEOUT,
                socket_connect_timeout=Config.REDIS_SOCKET_CONNECT_TIMEOUT,
                max_connections=Config.REDIS_MAX_CONNECTIONS,
                decode_responses=True,  
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            client = redis.Redis(connection_pool=cls._connection_pool)
            
            client.ping()
            print(f"Redis bağlantısı başarılı: {Config.REDIS_HOST}:{Config.REDIS_PORT}")
            
            return client
            
        except ConnectionError as e:
            print(f"Redis bağlantı hatası: {str(e)}")
            raise RuntimeError("Redis connection failed") from e
        except TimeoutError as e:
            print(f"Redis timeout hatası: {str(e)}")
            raise RuntimeError("Redis timeout") from e
        except Exception as e:
            print(f"Redis bilinmeyen hata: {str(e)}")
            raise RuntimeError("Redis error") from e

    @classmethod
    def close_connection(cls):
        if cls._client:
            cls._client.close()
            cls._client = None
        if cls._connection_pool:
            cls._connection_pool.disconnect()
            cls._connection_pool = None
        print("Redis bağlantısı kapatıldı")

    @classmethod
    def health_check(cls):
        try:
            client = cls.get_client()
            client.ping()
            return system_handshake(ResultCode.SUCCESS, "Redis sağlıklı")
        except Exception as e:
            return system_handshake(
                ResultCode.ERROR, 
                error_message=str(e), 
                function_name="redis_connection/health_check"
            )

    @classmethod
    def get_stats(cls):
        try:
            client = cls.get_client()
            info = client.info()
            
            stats = {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "0"),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "uptime_in_seconds": info.get("uptime_in_seconds", 0),
                "keyspace": client.dbsize()
            }
            
            return system_handshake(ResultCode.SUCCESS, data=stats)
        except Exception as e:
            return system_handshake(
                ResultCode.ERROR,
                error_message=str(e),
                function_name="redis_connection/get_stats"
            )


redis_client = RedisConnection.get_client()