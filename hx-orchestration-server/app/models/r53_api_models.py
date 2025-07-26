"""
Standardized API Models and Validators (R5.3 Compliance)
Provides consistent request/response models across all endpoints
"""
from pydantic import BaseModel, Field, validator
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from enum import Enum

class ServiceStatus(str, Enum):
    """Standard service status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    INITIALIZING = "initializing"
    SHUTTING_DOWN = "shutting_down"

class RequestPriority(str, Enum):
    """Standard request priority enumeration"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

class BaseRequest(BaseModel):
    """Standard base request model with common validation patterns"""
    request_id: str = Field(..., description="Unique request identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Request timestamp")
    priority: RequestPriority = Field(default=RequestPriority.NORMAL, description="Request priority")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    
    @validator('request_id')
    def validate_request_id(cls, v):
        if not v or len(v) < 8:
            raise ValueError('Request ID must be at least 8 characters')
        return v

class BaseResponse(BaseModel):
    """Standard base response model with consistent structure"""
    success: bool = Field(..., description="Operation success status")
    request_id: str = Field(..., description="Original request identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    error: Optional[str] = Field(None, description="Error message if failed")
    execution_time_ms: Optional[float] = Field(None, description="Processing time in milliseconds")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class HealthResponse(BaseModel):
    """Health check response model"""
    status: ServiceStatus = Field(..., description="Service health status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Health check timestamp")
    server_ip: str = Field(..., description="Server IP address")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class DetailedHealthResponse(HealthResponse):
    """Detailed health check response with system metrics"""
    system_metrics: Dict[str, float] = Field(..., description="System performance metrics")
    service_status: Dict[str, bool] = Field(..., description="External service status")
    uptime_seconds: float = Field(..., description="Service uptime in seconds")

class EmbeddingRequest(BaseRequest):
    """Embedding generation request model"""
    text: Union[str, List[str]] = Field(..., description="Text to embed")
    model: Optional[str] = Field("nomic-embed-text", description="Embedding model to use")
    options: Optional[Dict[str, Any]] = Field(None, description="Model-specific options")
    
    @validator('text')
    def validate_text(cls, v):
        if isinstance(v, str):
            if not v.strip():
                raise ValueError('Text cannot be empty')
            if len(v) > 100000:  # 100KB limit
                raise ValueError('Text too long (max 100KB)')
        elif isinstance(v, list):
            if not v:
                raise ValueError('Text list cannot be empty')
            for text in v:
                if not isinstance(text, str) or not text.strip():
                    raise ValueError('All texts must be non-empty strings')
        return v

class EmbeddingResponse(BaseResponse):
    """Embedding generation response model"""
    embeddings: Optional[List[List[float]]] = Field(None, description="Generated embeddings")
    model_used: Optional[str] = Field(None, description="Model that generated embeddings")
    cache_hit: Optional[bool] = Field(None, description="Whether result was cached")
    dimensions: Optional[int] = Field(None, description="Embedding dimensions")

class OrchestrationRequest(BaseRequest):
    """Orchestration workflow request model"""
    workflow_type: str = Field(..., description="Type of workflow to execute")
    input_data: Dict[str, Any] = Field(..., description="Input data for workflow")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Workflow parameters")
    
    @validator('workflow_type')
    def validate_workflow_type(cls, v):
        allowed_types = ['business_analysis', 'document_processing', 'ai_decision', 'multi_agent_coordination']
        if v not in allowed_types:
            raise ValueError(f'Workflow type must be one of: {", ".join(allowed_types)}')
        return v

class OrchestrationResponse(BaseResponse):
    """Orchestration workflow response model"""
    workflow_id: Optional[str] = Field(None, description="Workflow execution identifier")
    status: Optional[str] = Field(None, description="Workflow execution status")
    result: Optional[Dict[str, Any]] = Field(None, description="Workflow execution result")
    steps_completed: Optional[int] = Field(None, description="Number of completed steps")
    total_steps: Optional[int] = Field(None, description="Total number of steps")

class MetricsResponse(BaseModel):
    """Metrics collection response model"""
    service_metrics: Dict[str, Any] = Field(..., description="Service-specific metrics")
    system_metrics: Dict[str, Any] = Field(..., description="System performance metrics")
    business_metrics: Optional[Dict[str, Any]] = Field(None, description="Business process metrics")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Metrics collection timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ErrorResponse(BaseModel):
    """Standard error response model"""
    error_code: str = Field(..., description="Error code identifier")
    error_message: str = Field(..., description="Human-readable error message")
    error_details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    request_id: Optional[str] = Field(None, description="Associated request identifier")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
