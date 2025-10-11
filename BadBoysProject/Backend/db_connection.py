from pymongo import MongoClient

class MongoDB:
    _client = None

    @classmethod
    def client(cls):
        if cls._client is None:
            cls._client = MongoClient("mongodb://localhost:27017")
        return cls._client

client = MongoDB.client()