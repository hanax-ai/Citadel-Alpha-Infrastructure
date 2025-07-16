"""
External AI Model Data Models

Pydantic models for external AI model integration following HXP Governance Coding Standards.
Implements strong typing, validation, and data encapsulation for the 9 external AI models.

Author: Citadel AI Team
License: MIT
"""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum
import uuid

# Type aliases for better code readability
ModelId = str
JobId = str
ProcessingStatus = str


class ExternalModelType(Enum):
    """Supported external AI model types (Business rule encapsulation)."""
    OPENAI_GPT4 = "openai-gpt4"
    OPENAI_GPT35 = "openai-gpt3.5"
    ANTHROPIC_CLAUDE = "anthropic-claude"
    GOOGLE_GEMINI = "google-gemini"
    COHERE_COMMAND = "cohere-command"
    HUGGINGFACE_TRANSFORMERS = "huggingface-transformers"
    AZURE_OPENAI = "azure-openai"
    AWS_BEDROCK = "aws-bedrock"
    CUSTOM_API = "custom-api"


class IntegrationPattern(Enum):
    """Integration patterns for external models (Architecture encapsulation)."""
    REAL_TIME = "real_time"      # Direct API calls
    HYBRID = "hybrid"            # Cached + real-time
    BULK = "bulk"               # Batch processing


class ModelCapability(Enum):
    """Model capabilities (Feature encapsulation)."""
    TEXT_GENERATION = "text_generation"
    TEXT_EMBEDDING = "text_embedding"
    TEXT_CLASSIFICATION = "text_classification"
    QUESTION_ANSWERING = "question_answering"
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
    CODE_GENERATION = "code_generation"
    MULTIMODAL = "multimodal"


class ExternalModel(BaseModel):
    """
    External AI model configuration and metadata.
    
    Implements data encapsulation and validation following Single Responsibility Principle.
    """
    
    id: ModelId = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique model identifier"
    )
    
    name: str = Field(
        ...,
        description="Human-readable model name",
        min_length=1,
        max_length=255
    )
    
    model_type: ExternalModelType = Field(
        ...,
        description="Type of external model"
    )
    
    api_endpoint: str = Field(
        ...,
        description="API endpoint URL",
        min_length=1
    )
    
    api_key_name: Optional[str] = Field(
        None,
        description="Environment variable name for API key"
    )
    
    capabilities: List[ModelCapability] = Field(
        default_factory=list,
        description="List of model capabilities"
    )
    
    integration_pattern: IntegrationPattern = Field(
        default=IntegrationPattern.REAL_TIME,
        description="Integration pattern to use"
    )
    
    max_tokens: Optional[int] = Field(
        default=4096,
        description="Maximum tokens per request",
        ge=1,
        le=100000
    )
    
    rate_limit_rpm: Optional[int] = Field(
        default=60,
        description="Rate limit in requests per minute",
        ge=1,
        le=10000
    )
    
    timeout_seconds: int = Field(
        default=30,
        description="Request timeout in seconds",
        ge=1,
        le=300
    )
    
    retry_attempts: int = Field(
        default=3,
        description="Number of retry attempts",
        ge=0,
        le=10
    )
    
    cache_ttl_seconds: Optional[int] = Field(
        default=3600,
        description="Cache TTL for hybrid pattern",
        ge=0,
        le=86400
    )
    
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional model metadata"
    )
    
    config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Model-specific configuration"
    )
    
    is_active: bool = Field(
        default=True,
        description="Whether model is active"
    )
    
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Model registration timestamp"
    )
    
    updated_at: Optional[datetime] = Field(
        None,
        description="Last update timestamp"
    )
    
    @validator('api_endpoint')
    def validate_api_endpoint(cls, v):
        """Validate API endpoint URL format."""
        if not v.startswith(('http://', 'https://')):
            raise ValueError("API endpoint must be a valid HTTP/HTTPS URL")
        return v
    
    @validator('capabilities')
    def validate_capabilities(cls, v):
        """Validate model capabilities."""
        if not v:
            raise ValueError("Model must have at least one capability")
        return v
    
    def supports_capability(self, capability: ModelCapability) -> bool:
        """Check if model supports a specific capability."""
        return capability in self.capabilities
    
    def get_cache_key(self, request_data: str) -> str:
        """Generate cache key for request."""
        import hashlib
        key_data = f"{self.id}:{request_data}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "name": "OpenAI GPT-4",
                "model_type": "openai-gpt4",
                "api_endpoint": "https://api.openai.com/v1/chat/completions",
                "api_key_name": "OPENAI_API_KEY",
                "capabilities": ["text_generation", "question_answering"],
                "integration_pattern": "hybrid",
                "max_tokens": 4096,
                "rate_limit_rpm": 60
            }
        }


class BatchJob(BaseModel):
    """
    Batch processing job for external models.
    
    Encapsulates batch job parameters and status tracking.
    """
    
    id: JobId = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique job identifier"
    )
    
    model_id: ModelId = Field(
        ...,
        description="External model ID to use"
    )
    
    job_type: str = Field(
        ...,
        description="Type of batch job",
        min_length=1,
        max_length=100
    )
    
    input_data: List[Dict[str, Any]] = Field(
        ...,
        description="Input data for batch processing",
        min_items=1
    )
    
    output_data: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Output data from batch processing"
    )
    
    status: str = Field(
        default="pending",
        description="Job status",
        regex="^(pending|running|completed|failed|cancelled)$"
    )
    
    progress: float = Field(
        default=0.0,
        description="Job progress percentage",
        ge=0.0,
        le=100.0
    )
    
    total_items: int = Field(
        default=0,
        description="Total number of items to process",
        ge=0
    )
    
    processed_items: int = Field(
        default=0,
        description="Number of items processed",
        ge=0
    )
    
    failed_items: int = Field(
        default=0,
        description="Number of failed items",
        ge=0
    )
    
    error_messages: List[str] = Field(
        default_factory=list,
        description="List of error messages"
    )
    
    config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Job-specific configuration"
    )
    
    priority: int = Field(
        default=5,
        description="Job priority (1-10, higher is more priority)",
        ge=1,
        le=10
    )
    
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Job creation timestamp"
    )
    
    started_at: Optional[datetime] = Field(
        None,
        description="Job start timestamp"
    )
    
    completed_at: Optional[datetime] = Field(
        None,
        description="Job completion timestamp"
    )
    
    estimated_completion: Optional[datetime] = Field(
        None,
        description="Estimated completion time"
    )
    
    @validator('input_data')
    def validate_input_data(cls, v):
        """Validate input data structure."""
        if not v:
            raise ValueError("Input data cannot be empty")
        
        # Ensure all items have required fields
        for i, item in enumerate(v):
            if not isinstance(item, dict):
                raise ValueError(f"Input item {i} must be a dictionary")
            if 'id' not in item:
                item['id'] = str(uuid.uuid4())
        
        return v
    
    def update_progress(self, processed: int, failed: int = 0) -> None:
        """Update job progress."""
        self.processed_items = processed
        self.failed_items = failed
        
        if self.total_items > 0:
            self.progress = (processed / self.total_items) * 100
        
        if processed + failed >= self.total_items:
            self.status = "completed" if failed == 0 else "completed"
            self.completed_at = datetime.now()
    
    def add_error(self, error_message: str) -> None:
        """Add error message to job."""
        self.error_messages.append(error_message)
        self.failed_items += 1
    
    def get_success_rate(self) -> float:
        """Calculate job success rate."""
        if self.total_items == 0:
            return 0.0
        return ((self.processed_items - self.failed_items) / self.total_items) * 100
    
    def get_duration(self) -> Optional[float]:
        """Get job duration in seconds."""
        if not self.started_at:
            return None
        
        end_time = self.completed_at or datetime.now()
        return (end_time - self.started_at).total_seconds()
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "model_id": "model_123",
                "job_type": "text_generation",
                "input_data": [
                    {"id": "1", "prompt": "Hello world"},
                    {"id": "2", "prompt": "How are you?"}
                ],
                "status": "pending",
                "priority": 5
            }
        }


class ModelResponse(BaseModel):
    """
    Response from external model API call.
    
    Standardized response format for all external models.
    """
    
    model_id: ModelId = Field(
        ...,
        description="Model that generated the response"
    )
    
    request_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique request identifier"
    )
    
    response_data: Dict[str, Any] = Field(
        ...,
        description="Response data from model"
    )
    
    success: bool = Field(
        default=True,
        description="Whether request was successful"
    )
    
    error_message: Optional[str] = Field(
        None,
        description="Error message if request failed"
    )
    
    processing_time_ms: float = Field(
        default=0.0,
        description="Processing time in milliseconds",
        ge=0.0
    )
    
    tokens_used: Optional[int] = Field(
        None,
        description="Number of tokens used",
        ge=0
    )
    
    cost_estimate: Optional[float] = Field(
        None,
        description="Estimated cost in USD",
        ge=0.0
    )
    
    cached: bool = Field(
        default=False,
        description="Whether response was served from cache"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Response timestamp"
    )
    
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional response metadata"
    )
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ModelUsageStats(BaseModel):
    """
    Usage statistics for external models.
    
    Tracks model usage metrics and performance.
    """
    
    model_id: ModelId = Field(
        ...,
        description="Model identifier"
    )
    
    total_requests: int = Field(
        default=0,
        description="Total number of requests",
        ge=0
    )
    
    successful_requests: int = Field(
        default=0,
        description="Number of successful requests",
        ge=0
    )
    
    failed_requests: int = Field(
        default=0,
        description="Number of failed requests",
        ge=0
    )
    
    total_tokens: int = Field(
        default=0,
        description="Total tokens processed",
        ge=0
    )
    
    total_cost: float = Field(
        default=0.0,
        description="Total cost in USD",
        ge=0.0
    )
    
    average_response_time_ms: float = Field(
        default=0.0,
        description="Average response time in milliseconds",
        ge=0.0
    )
    
    cache_hit_rate: float = Field(
        default=0.0,
        description="Cache hit rate percentage",
        ge=0.0,
        le=100.0
    )
    
    last_used: Optional[datetime] = Field(
        None,
        description="Last usage timestamp"
    )
    
    period_start: datetime = Field(
        default_factory=datetime.now,
        description="Statistics period start"
    )
    
    period_end: Optional[datetime] = Field(
        None,
        description="Statistics period end"
    )
    
    def get_success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
    
    def get_failure_rate(self) -> float:
        """Calculate failure rate percentage."""
        if self.total_requests == 0:
            return 0.0
        return (self.failed_requests / self.total_requests) * 100
    
    def get_average_cost_per_request(self) -> float:
        """Calculate average cost per request."""
        if self.total_requests == 0:
            return 0.0
        return self.total_cost / self.total_requests
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
