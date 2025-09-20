from loguru import logger
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from setting import Settings


class MongoDatabaseConnector:
    _instance: MongoClient | None = None
    
    def __new__(cls, *args, **kwargs) -> MongoClient:
        if cls._instance is None:
            try:
                settings = Settings.load_settings()
                cls._instance = MongoClient(settings.DATABASE_HOST)
            except ConnectionFailure as e:
                logger.error(f"Could not connect to MongoDB: {e}")
                raise
            
        logger.info(f"Connection to MongoDB with URI successful: {settings.DATABASE_HOST}")
        return cls._instance

connection = MongoDatabaseConnector()