"""
REST API Models
==============

Pydantic models for REST API request/response schemas.
Provides data validation and serialization for FastAPI endpoints.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum


class DistanceMetric(str, Enum):
    """Distance metric enumeration."""
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    DOT = "dot"
    MANHATTAN = "manhattan"


class OperationType(str, Enum):
    """Operation type enumeration."""
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    UPSERT = "upsert"


class HealthStatus(str, Enum):
    """Health status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class VectorModel(BaseModel):
    """Vector data model."""
    id: Optional[str] = None
    vector: List[float] = Field(..., description="Vector data", min_items=1)
    payload: Optional[Dict[str, Any]] = Field(None, description="Vector metadata")
    collection: Optional[str] = Field(None, description="Collection name")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @validator('vector')
    def validate_vector(cls, v):
        """Validate vector data."""
        if not v:
            raise ValueError("Vector cannot be empty")
        
        for i, val in enumerate(v):
            if not isinstance(val, (int, float)):
                raise ValueError(f"Vector element at index {i} must be a number")
            
            if val != val:  # Check for NaN
                raise ValueError(f"Vector element at index {i} cannot be NaN")
        
        return v
    
    @validator('payload')
    def validate_payload(cls, v):
        """Validate payload size."""
        if v is not None:
            payload_str = str(v)
            if len(payload_str) > 1024 * 1024:  # 1MB limit
                raise ValueError("Payload size exceeds 1MB limit")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "id": "vector_001",
                "vector": [0.1, 0.2, 0.3, 0.4],
                "payload": {"category": "document", "title": "Example"},
                "collection": "documents"
            }
        }


class CollectionConfigModel(BaseModel):
    """Collection configuration model."""
    vector_size: int = Field(..., description="Vector dimension", gt=0, le=65536)
    distance: DistanceMetric = Field(DistanceMetric.COSINE, description="Distance metric")
    shard_number: Optional[int] = Field(1, description="Number of shards", gt=0)
    replication_factor: Optional[int] = Field(1, description="Replication factor", gt=0)
    write_consistency_factor: Optional[int] = Field(1, description="Write consistency factor", gt=0)
    
    class Config:
        schema_extra = {
            "example": {
                "vector_size": 384,
                "distance": "cosine",
                "shard_number": 1,
                "replication_factor": 1
            }
        }


class CollectionModel(BaseModel):
    """Collection information model."""
    name: str = Field(..., description="Collection name")
    vector_size: int = Field(..., description="Vector dimension")
    distance: str = Field(..., description="Distance metric")
    points_count: int = Field(..., description="Number of points")
    indexed_vectors_count: int = Field(..., description="Number of indexed vectors")
    status: str = Field(..., description="Collection status")
    optimizer_status: Optional[Dict[str, Any]] = Field(None, description="Optimizer status")
    created_at: Optional[datetime] = None
    
    class Config:
        schema_extra = {
            "example": {
                "name": "documents",
                "vector_size": 384,
                "distance": "cosine",
                "points_count": 1000,
                "indexed_vectors_count": 1000,
                "status": "active"
            }
        }


class SearchRequestModel(BaseModel):
    """Search request model."""
    vector: List[float] = Field(..., description="Query vector", min_items=1)
    limit: int = Field(10, description="Maximum results", gt=0, le=10000)
    offset: int = Field(0, description="Results offset", ge=0)
    filter: Optional[Dict[str, Any]] = Field(None, description="Search filter")
    score_threshold: Optional[float] = Field(None, description="Minimum score threshold", ge=0, le=1)
    with_payload: bool = Field(True, description="Include payload in results")
    with_vector: bool = Field(False, description="Include vector in results")
    
    @validator('vector')
    def validate_vector(cls, v):
        """Validate query vector."""
        if not v:
            raise ValueError("Query vector cannot be empty")
        
        for i, val in enumerate(v):
            if not isinstance(val, (int, float)):
                raise ValueError(f"Vector element at index {i} must be a number")
            
            if val != val:  # Check for NaN
                raise ValueError(f"Vector element at index {i} cannot be NaN")
        
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "vector": [0.1, 0.2, 0.3, 0.4],
                "limit": 10,
                "offset": 0,
                "filter": {"category": "document"},
                "score_threshold": 0.7,
                "with_payload": True,
                "with_vector": False
            }
        }


class SearchResultModel(BaseModel):
    """Search result model."""
    id: str = Field(..., description="Vector ID")
    score: float = Field(..., description="Similarity score")
    payload: Optional[Dict[str, Any]] = Field(None, description="Vector metadata")
    vector: Optional[List[float]] = Field(None, description="Vector data")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "vector_001",
                "score": 0.95,
                "payload": {"category": "document", "title": "Example"},
                "vector": [0.1, 0.2, 0.3, 0.4]
            }
        }


class SearchResponseModel(BaseModel):
    """Search response model."""
    results: List[SearchResultModel] = Field(..., description="Search results")
    total_count: int = Field(..., description="Total matching results")
    query_time: float = Field(..., description="Query execution time in seconds")
    collection: str = Field(..., description="Collection name")
    
    class Config:
        schema_extra = {
            "example": {
                "results": [
                    {
                        "id": "vector_001",
                        "score": 0.95,
                        "payload": {"category": "document"},
                        "vector": None
                    }
                ],
                "total_count": 1,
                "query_time": 0.005,
                "collection": "documents"
            }
        }


class BatchRequestModel(BaseModel):
    """Batch operation request model."""
    operation: OperationType = Field(..., description="Batch operation type")
    vectors: List[VectorModel] = Field(..., description="Vector data", min_items=1)
    
    @validator('vectors')
    def validate_batch_size(cls, v):
        """Validate batch size."""
        if len(v) > 10000:
            raise ValueError("Batch size cannot exceed 10000")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "operation": "insert",
                "vectors": [
                    {
                        "id": "vector_001",
                        "vector": [0.1, 0.2, 0.3, 0.4],
                        "payload": {"category": "document"}
                    }
                ]
            }
        }


class BatchResponseModel(BaseModel):
    """Batch operation response model."""
    operation: str = Field(..., description="Operation type")
    success_count: int = Field(..., description="Number of successful operations")
    failed_count: int = Field(..., description="Number of failed operations")
    total_count: int = Field(..., description="Total number of operations")
    errors: Optional[List[str]] = Field(None, description="Error messages")
    duration: float = Field(..., description="Operation duration in seconds")
    
    class Config:
        schema_extra = {
            "example": {
                "operation": "insert",
                "success_count": 100,
                "failed_count": 0,
                "total_count": 100,
                "errors": None,
                "duration": 0.5
            }
        }


class HealthCheckModel(BaseModel):
    """Health check model."""
    name: str = Field(..., description="Health check name")
    status: HealthStatus = Field(..., description="Health status")
    message: str = Field(..., description="Status message")
    last_check: datetime = Field(..., description="Last check timestamp")
    duration: float = Field(..., description="Check duration in seconds")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "qdrant_connection",
                "status": "healthy",
                "message": "Connection is healthy",
                "last_check": "2024-01-01T12:00:00Z",
                "duration": 0.005,
                "details": {"host": "192.168.10.30", "port": 6333}
            }
        }


class HealthStatusModel(BaseModel):
    """System health status model."""
    status: HealthStatus = Field(..., description="Overall health status")
    timestamp: datetime = Field(..., description="Status timestamp")
    last_check: datetime = Field(..., description="Last check timestamp")
    checks: Dict[str, HealthCheckModel] = Field(..., description="Individual health checks")
    summary: Dict[str, Any] = Field(..., description="Health summary")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2024-01-01T12:00:00Z",
                "last_check": "2024-01-01T12:00:00Z",
                "checks": {
                    "qdrant_connection": {
                        "name": "qdrant_connection",
                        "status": "healthy",
                        "message": "Connection is healthy",
                        "last_check": "2024-01-01T12:00:00Z",
                        "duration": 0.005
                    }
                },
                "summary": {
                    "total_checks": 1,
                    "healthy_checks": 1,
                    "unhealthy_checks": 0
                }
            }
        }


class MetricModel(BaseModel):
    """Metric model."""
    name: str = Field(..., description="Metric name")
    value: float = Field(..., description="Metric value")
    labels: Optional[Dict[str, str]] = Field(None, description="Metric labels")
    timestamp: datetime = Field(..., description="Metric timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "vector_search_duration",
                "value": 0.005,
                "labels": {"collection": "documents", "operation": "search"},
                "timestamp": "2024-01-01T12:00:00Z"
            }
        }


class ErrorResponseModel(BaseModel):
    """Error response model."""
    error_type: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "error_type": "ValidationError",
                "message": "Vector dimension mismatch",
                "error_code": "VECTOR_001",
                "details": {"expected": 384, "actual": 256},
                "timestamp": "2024-01-01T12:00:00Z"
            }
        }


class CollectionStatsModel(BaseModel):
    """Collection statistics model."""
    collection: str = Field(..., description="Collection name")
    points_count: int = Field(..., description="Number of points")
    indexed_vectors_count: int = Field(..., description="Number of indexed vectors")
    memory_usage: Optional[int] = Field(None, description="Memory usage in bytes")
    disk_usage: Optional[int] = Field(None, description="Disk usage in bytes")
    avg_vector_size: Optional[float] = Field(None, description="Average vector size")
    last_updated: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "collection": "documents",
                "points_count": 1000,
                "indexed_vectors_count": 1000,
                "memory_usage": 1048576,
                "disk_usage": 2097152,
                "avg_vector_size": 384.0,
                "last_updated": "2024-01-01T12:00:00Z"
            }
        }


class DeleteRequestModel(BaseModel):
    """Delete request model."""
    ids: List[str] = Field(..., description="Vector IDs to delete", min_items=1)
    
    @validator('ids')
    def validate_ids(cls, v):
        """Validate ID list."""
        if len(v) > 10000:
            raise ValueError("Cannot delete more than 10000 vectors at once")
        
        for i, id_val in enumerate(v):
            if not isinstance(id_val, str) or not id_val.strip():
                raise ValueError(f"ID at index {i} must be a non-empty string")
        
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "ids": ["vector_001", "vector_002", "vector_003"]
            }
        }


class UpdateRequestModel(BaseModel):
    """Update request model."""
    id: str = Field(..., description="Vector ID to update")
    vector: Optional[List[float]] = Field(None, description="New vector data")
    payload: Optional[Dict[str, Any]] = Field(None, description="New payload data")
    
    @validator('vector')
    def validate_vector(cls, v):
        """Validate vector data."""
        if v is not None:
            if not v:
                raise ValueError("Vector cannot be empty")
            
            for i, val in enumerate(v):
                if not isinstance(val, (int, float)):
                    raise ValueError(f"Vector element at index {i} must be a number")
                
                if val != val:  # Check for NaN
                    raise ValueError(f"Vector element at index {i} cannot be NaN")
        
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "id": "vector_001",
                "vector": [0.1, 0.2, 0.3, 0.4],
                "payload": {"category": "updated_document"}
            }
        }


class ScrollRequestModel(BaseModel):
    """Scroll request model."""
    limit: int = Field(100, description="Number of results per page", gt=0, le=10000)
    offset: Optional[str] = Field(None, description="Scroll offset token")
    filter: Optional[Dict[str, Any]] = Field(None, description="Filter criteria")
    with_payload: bool = Field(True, description="Include payload in results")
    with_vector: bool = Field(False, description="Include vector in results")
    
    class Config:
        schema_extra = {
            "example": {
                "limit": 100,
                "offset": None,
                "filter": {"category": "document"},
                "with_payload": True,
                "with_vector": False
            }
        }


class ScrollResponseModel(BaseModel):
    """Scroll response model."""
    points: List[VectorModel] = Field(..., description="Vector points")
    next_offset: Optional[str] = Field(None, description="Next page offset token")
    total_count: Optional[int] = Field(None, description="Total number of points")
    
    class Config:
        schema_extra = {
            "example": {
                "points": [
                    {
                        "id": "vector_001",
                        "vector": [0.1, 0.2, 0.3, 0.4],
                        "payload": {"category": "document"}
                    }
                ],
                "next_offset": "eyJpZCI6InZlY3Rvcl8xMDAifQ==",
                "total_count": 1000
            }
        }


# Response models for common HTTP status codes
class SuccessResponseModel(BaseModel):
    """Success response model."""
    success: bool = Field(True, description="Operation success status")
    message: str = Field(..., description="Success message")
    data: Optional[Any] = Field(None, description="Response data")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "data": None
            }
        }


# Model validation utilities
def validate_vector_dimension(vector: List[float], expected_dim: int) -> bool:
    """Validate vector dimension."""
    return len(vector) == expected_dim


def validate_collection_name(name: str) -> bool:
    """Validate collection name format."""
    import re
    return bool(re.match(r'^[a-zA-Z0-9_-]+$', name))


def create_error_response(error_type: str, message: str, 
                         error_code: Optional[str] = None,
                         details: Optional[Dict[str, Any]] = None) -> ErrorResponseModel:
    """Create standardized error response."""
    return ErrorResponseModel(
        error_type=error_type,
        message=message,
        error_code=error_code,
        details=details
    )


# Model conversion utilities
def vector_to_dict(vector: VectorModel) -> Dict[str, Any]:
    """Convert vector model to dictionary."""
    return vector.dict(exclude_none=True)


def dict_to_vector(data: Dict[str, Any]) -> VectorModel:
    """Convert dictionary to vector model."""
    return VectorModel(**data)


# Batch processing utilities
def split_batch(vectors: List[VectorModel], batch_size: int = 1000) -> List[List[VectorModel]]:
    """Split vector batch into smaller chunks."""
    return [vectors[i:i + batch_size] for i in range(0, len(vectors), batch_size)]


def merge_batch_responses(responses: List[BatchResponseModel]) -> BatchResponseModel:
    """Merge multiple batch responses."""
    total_success = sum(r.success_count for r in responses)
    total_failed = sum(r.failed_count for r in responses)
    total_count = sum(r.total_count for r in responses)
    total_duration = sum(r.duration for r in responses)
    
    all_errors = []
    for r in responses:
        if r.errors:
            all_errors.extend(r.errors)
    
    return BatchResponseModel(
        operation=responses[0].operation if responses else "unknown",
        success_count=total_success,
        failed_count=total_failed,
        total_count=total_count,
        errors=all_errors if all_errors else None,
        duration=total_duration
    )
