import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv
from config import Config

load_dotenv()

class MongoDB:
    _client = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            cls._client = cls._create_client()
        return cls._client

    @staticmethod
    def _create_client():
        host = Config.MONGO_HOST
        port = Config.MONGO_PORT
        user = Config.MONGO_USER
        password = Config.MONGO_PASSWORD
        db_name = Config.MONGO_DB

        tls_enabled = Config.MONGO_TLS
        tls_ca_file = Config.MONGO_TLS_CA_FILE
        tls_cert_file = Config.MONGO_TLS_CERT_FILE

        if not all([user, password, db_name]):
            raise RuntimeError("MongoDB bilgilerine ulaşılamadı.")

        if tls_enabled and not tls_ca_file:
            raise RuntimeError("TLS açık ancak CA sertifikasına ulaşılamadı.")

        uri = (
            f"mongodb://{user}:{password}@{host}:{port}/"
            f"{db_name}?authSource={db_name}"
        )

        client_kwargs = {
            "serverSelectionTimeoutMS": Config.MONGO_SERVER_SELECTION_TIMEOUT,
            "connectTimeoutMS": Config.MONGO_CONNECT_TIMEOUT,
            "socketTimeoutMS": Config.MONGO_SOCKET_TIMEOUT,
            "maxPoolSize": Config.MONGO_MAX_POOL_SIZE,
            "minPoolSize": Config.MONGO_MIN_POOL_SIZE,
            "retryWrites": True,
            "retryReads": True,
        }


        if tls_enabled:
            client_kwargs.update({
                "tls": True,
                "tlsCAFile": tls_ca_file,
                "tlsCertificateKeyFile": tls_cert_file
            })

        try:
            return MongoClient(uri, **client_kwargs)
        except ConnectionFailure as e:
            raise RuntimeError("MongoDB connection failed") from e
        
client = MongoDB.get_client()
