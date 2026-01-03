import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv

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
        host = os.getenv("MONGO_HOST", "localhost")
        port = int(os.getenv("MONGO_PORT", 27017))
        user = os.getenv("MONGO_USER")
        password = os.getenv("MONGO_PASSWORD")
        db_name = os.getenv("MONGO_DB")

        tls_enabled = os.getenv("MONGO_TLS", "false").lower() == "true"
        tls_ca_file = os.getenv("MONGO_TLS_CA_FILE")
        tls_cert_file = os.getenv("MONGO_TLS_CERT_FILE")

        if not all([user, password, db_name]):
            raise RuntimeError("MongoDB bilgilerine ulaşılamadı.")

        if tls_enabled and not tls_ca_file:
            raise RuntimeError("TLS açık ancak CA sertifikasına ulaşılamadı.")

        uri = (
            f"mongodb://{user}:{password}@{host}:{port}/"
            f"{db_name}?authSource={db_name}"
        )

        client_kwargs = {
            "serverSelectionTimeoutMS": 3000,
            "connectTimeoutMS": 5000,
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
