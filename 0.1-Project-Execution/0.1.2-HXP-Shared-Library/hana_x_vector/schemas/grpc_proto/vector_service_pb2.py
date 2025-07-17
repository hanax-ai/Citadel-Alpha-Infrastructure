"""
Generated protocol buffer code for vector_service.proto
"""

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from typing import List, Dict, Any, Optional

# This is a minimal implementation to satisfy imports
# In a real deployment, these would be generated from .proto files

class VectorRequest(_message.Message):
    """Vector request message."""
    
    def __init__(self, id: str = "", vector: List[float] = None, 
                 payload: Dict[str, Any] = None, collection: str = ""):
        self.id = id
        self.vector = vector or []
        self.payload = payload or {}
        self.collection = collection

class VectorResponse(_message.Message):
    """Vector response message."""
    
    def __init__(self, success: bool = False, message: str = "", 
                 vector_id: str = "", score: float = 0.0):
        self.success = success
        self.message = message
        self.vector_id = vector_id
        self.score = score

class SearchRequest(_message.Message):
    """Search request message."""
    
    def __init__(self, vector: List[float] = None, collection: str = "", 
                 limit: int = 10, filter: Dict[str, Any] = None):
        self.vector = vector or []
        self.collection = collection
        self.limit = limit
        self.filter = filter or {}

class SearchResponse(_message.Message):
    """Search response message."""
    
    def __init__(self, results: List[Dict[str, Any]] = None, 
                 total_count: int = 0, query_time: float = 0.0):
        self.results = results or []
        self.total_count = total_count
        self.query_time = query_time

class CollectionRequest(_message.Message):
    """Collection request message."""
    
    def __init__(self, name: str = "", dimension: int = 0, 
                 distance_metric: str = "cosine"):
        self.name = name
        self.dimension = dimension
        self.distance_metric = distance_metric

class CollectionResponse(_message.Message):
    """Collection response message."""
    
    def __init__(self, success: bool = False, message: str = "", 
                 collection_name: str = ""):
        self.success = success
        self.message = message
        self.collection_name = collection_name

class HealthRequest(_message.Message):
    """Health check request message."""
    
    def __init__(self):
        pass

class HealthResponse(_message.Message):
    """Health check response message."""
    
    def __init__(self, status: str = "OK", version: str = "1.0.0"):
        self.status = status
        self.version = version
