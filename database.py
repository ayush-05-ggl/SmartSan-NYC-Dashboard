"""MongoDB database connection and utilities."""
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from config import config
import logging

logger = logging.getLogger(__name__)

class Database:
    """MongoDB database connection manager."""
    
    _client = None
    _db = None
    
    @classmethod
    def connect(cls, config_name='default'):
        """Connect to MongoDB."""
        cfg = config[config_name]()
        
        try:
            cls._client = MongoClient(
                cfg.MONGODB_URI,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                tlsAllowInvalidCertificates=True  # For development/testing
            )
            # Test connection
            cls._client.admin.command('ping')
            cls._db = cls._client[cfg.MONGODB_DB_NAME]
            logger.info(f"Connected to MongoDB: {cfg.MONGODB_DB_NAME}")
            return cls._db
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"MongoDB connection failed: {e}")
            raise
    
    @classmethod
    def get_db(cls):
        """Get database instance."""
        if cls._db is None:
            cls.connect()
        return cls._db
    
    @classmethod
    def disconnect(cls):
        """Close MongoDB connection."""
        if cls._client:
            cls._client.close()
            logger.info("Disconnected from MongoDB")

