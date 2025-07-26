"""
R5.3 API Models
Standardized Pydantic models for API requests and responses
"""

from pydantic import BaseModel, Field, validator, ConfigDict
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from enum import Enum

# Base Models
class BaseRequest(BaseModel):
    """Base class for all API requests."""
    
    model_config = ConfigDict(
        protected_namespaces=(),
        validate_assignment=True,
        use_enum_values=True
    )
    
    request_id: Optional[str] = Field(None, description="Unique request identifier")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow, description="Request timestamp")

class BaseResponse(BaseModel):
    """Base class for all API responses."""
    
    model_config = ConfigDict(
        protected_namespaces=(),
        validate_assignment=True,
        use_enum_values=True
    )
    
    success: bool = Field(..., description="Whether the request was successful")
    message: str = Field(default="", description="Response message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

# Health Check Models
class HealthStatus(str, Enum):
    """Health status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

class ServiceHealth(BaseModel):
    """Model for individual service health."""
    name: str = Field(..., description="Service name")
    status: HealthStatus = Field(..., description="Service health status")
    response_time: Optional[float] = Field(None, description="Service response time in seconds")
    last_check: datetime = Field(default_factory=datetime.utcnow, description="Last health check timestamp")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional health details")

class HealthResponse(BaseResponse):
    """Response model for health checks."""
    status: HealthStatus = Field(..., description="Overall system health status")
    services: List[ServiceHealth] = Field(default_factory=list, description="Individual service health status")
    system_info: Optional[Dict[str, Any]] = Field(None, description="System information")
    uptime: Optional[float] = Field(None, description="System uptime in seconds")

# Embedding Models
class EmbeddingRequest(BaseRequest):
    """Request model for embedding operations."""
    
    text: str = Field(..., description="Text to embed", min_length=1, max_length=10000)
    llm_model: str = Field(..., description="Model to use for embedding", alias="model")
    normalize: bool = Field(default=True, description="Whether to normalize embeddings")
    
    @validator('text')
    def validate_text(cls, v):
        if not v.strip():
            raise ValueError('Text cannot be empty or whitespace only')
        return v.strip()

class EmbeddingResponse(BaseResponse):
    """Response model for embedding operations."""
    embedding: List[float] = Field(..., description="Generated embedding vector")
    model_used: str = Field(..., description="Model used for embedding")
    dimensions: int = Field(..., description="Embedding vector dimensions")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")

class BatchEmbeddingRequest(BaseRequest):
    """Request model for batch embedding operations."""
    
    texts: List[str] = Field(..., description="List of texts to embed", min_items=1, max_items=100)
    llm_model: str = Field(..., description="Model to use for embedding", alias="model")
    normalize: bool = Field(default=True, description="Whether to normalize embeddings")
    
    @validator('texts')
    def validate_texts(cls, v):
        if not v:
            raise ValueError('Texts list cannot be empty')
        
        for i, text in enumerate(v):
            if not text.strip():
                raise ValueError(f'Text at index {i} cannot be empty or whitespace only')
            if len(text) > 10000:
                raise ValueError(f'Text at index {i} exceeds maximum length of 10,000 characters')
        
        return [text.strip() for text in v]

class BatchEmbeddingResponse(BaseResponse):
    """Response model for batch embedding operations."""
    embeddings: List[List[float]] = Field(..., description="Generated embedding vectors")
    model_used: str = Field(..., description="Model used for embedding")
    dimensions: int = Field(..., description="Embedding vector dimensions")
    count: int = Field(..., description="Number of embeddings generated")
    processing_time: Optional[float] = Field(None, description="Total processing time in seconds")

# Orchestration Models
class OrchestrationRequest(BaseRequest):
    """Request model for orchestration operations."""
    
    operation: str = Field(..., description="Operation to perform")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Operation parameters")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    
    @validator('operation')
    def validate_operation(cls, v):
        allowed_operations = ['process', 'analyze', 'generate', 'transform']
        if v not in allowed_operations:
            raise ValueError(f'Operation must be one of: {", ".join(allowed_operations)}')
        return v

class OrchestrationResponse(BaseResponse):
    """Response model for orchestration operations."""
    operation: str = Field(..., description="Performed operation")
    result: Dict[str, Any] = Field(..., description="Operation result")
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

# Model Information Models
class ModelInfo(BaseModel):
    """Model information."""
    name: str = Field(..., description="Model name")
    type: str = Field(..., description="Model type (e.g., embedding, language)")
    dimensions: Optional[int] = Field(None, description="Vector dimensions for embedding models")
    max_tokens: Optional[int] = Field(None, description="Maximum token limit")
    description: Optional[str] = Field(None, description="Model description")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional model metadata")

class ModelsResponse(BaseResponse):
    """Response model for listing available models."""
    models: List[ModelInfo] = Field(..., description="Available models")
    count: int = Field(..., description="Number of available models")

# Error Models
class ErrorDetail(BaseModel):
    """Detailed error information."""
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    field: Optional[str] = Field(None, description="Field that caused the error")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional error context")

class ErrorResponse(BaseResponse):
    """Response model for errors."""
    success: bool = Field(default=False, description="Always false for error responses")
    error_code: str = Field(..., description="Error code")
    error_message: str = Field(..., description="Error message")
    details: Optional[List[ErrorDetail]] = Field(None, description="Detailed error information")
    
# Metrics Models
class MetricPoint(BaseModel):
    """Single metric data point."""
    name: str = Field(..., description="Metric name")
    value: Union[int, float] = Field(..., description="Metric value")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Metric timestamp")
    tags: Optional[Dict[str, str]] = Field(None, description="Metric tags")

class MetricsResponse(BaseResponse):
    """Response model for metrics."""
    metrics: List[MetricPoint] = Field(..., description="Metric data points")
    time_range: Optional[Dict[str, datetime]] = Field(None, description="Time range for metrics")

# Authentication Models
class AuthRequest(BaseModel):
    """Authentication request model."""
    username: Optional[str] = Field(None, description="Username")
    password: Optional[str] = Field(None, description="Password")
    token: Optional[str] = Field(None, description="Authentication token")
    api_key: Optional[str] = Field(None, description="API key")

class AuthResponse(BaseResponse):
    """Authentication response model."""
    authenticated: bool = Field(..., description="Whether authentication was successful")
    token: Optional[str] = Field(None, description="Access token")
    expires_at: Optional[datetime] = Field(None, description="Token expiration time")
    permissions: Optional[List[str]] = Field(None, description="User permissions")

# System Information Models
class SystemInfo(BaseModel):
    """System information model."""
    version: str = Field(..., description="Application version")
    environment: str = Field(..., description="Environment (dev, prod, etc.)")
    uptime: float = Field(..., description="System uptime in seconds")
    memory_usage: Optional[Dict[str, Any]] = Field(None, description="Memory usage statistics")
    cpu_usage: Optional[float] = Field(None, description="CPU usage percentage")
    disk_usage: Optional[Dict[str, Any]] = Field(None, description="Disk usage statistics")

class SystemInfoResponse(BaseResponse):
    """System information response."""
    system: SystemInfo = Field(..., description="System information")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Information timestamp")
