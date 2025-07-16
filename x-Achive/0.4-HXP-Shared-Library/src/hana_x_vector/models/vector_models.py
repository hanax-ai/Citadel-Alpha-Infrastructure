"""
Vector Data Models

Pydantic models for vector database operations following HXP Governance Coding Standards.
Implements strong typing, validation, and data encapsulation principles.

Author: Citadel AI Team
License: MIT
"""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum
import uuid

# Type aliases for better code readability
VectorId = Union[str, int]
Embedding = List[float]
Metadata = Dict[str, Any]


class VectorDimension(Enum):
    """Supported vector dimensions (Business rule encapsulation)."""
    DIM_384 = 384      # all-MiniLM-L6-v2
    DIM_768 = 768      # phi-3-mini, e5-small
    DIM_1024 = 1024    # bge-base
    DIM_1536 = 1536    # OpenAI embeddings
    DIM_4096 = 4096    # Large models


class Vector(BaseModel):
    """
    Vector data model with strong typing and validation.
    
    Implements data encapsulation and validation following Single Responsibility Principle.
    """
    
    id: VectorId = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique vector identifier"
    )
    
    embedding: Embedding = Field(
        ...,
        description="Vector embedding values",
        min_items=1,
        max_items=4096
    )
    
    metadata: Optional[Metadata] = Field(
        default_factory=dict,
        description="Additional vector metadata"
    )
    
    collection: Optional[str] = Field(
        None,
        description="Collection name this vector belongs to"
    )
    
    score: Optional[float] = Field(
        None,
        description="Similarity score (for search results)",
        ge=0.0,
        le=1.0
    )
    
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Vector creation timestamp"
    )
    
    updated_at: Optional[datetime] = Field(
        None,
        description="Last update timestamp"
    )
    
    @validator('embedding')
    def validate_embedding_dimension(cls, v):
        """Validate embedding dimension against supported dimensions."""
        if len(v) not in [dim.value for dim in VectorDimension]:
            raise ValueError(f"Unsupported embedding dimension: {len(v)}")
        return v
    
    @validator('metadata')
    def validate_metadata(cls, v):
        """Validate metadata structure."""
        if v is None:
            return {}
        
        # Ensure metadata values are JSON serializable
        try:
            import json
            json.dumps(v)
        except (TypeError, ValueError) as e:
            raise ValueError(f"Metadata must be JSON serializable: {e}")
        
        return v
    
    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return len(self.embedding)
    
    def update_metadata(self, new_metadata: Metadata) -> None:
        """Update vector metadata."""
        self.metadata.update(new_metadata)
        self.updated_at = datetime.now()
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "id": "vec_123",
                "embedding": [0.1, 0.2, 0.3],
                "metadata": {"text": "sample text", "category": "document"},
                "collection": "documents",
                "score": 0.95
            }
        }


class VectorSearchRequest(BaseModel):
    """
    Vector search request model with validation.
    
    Encapsulates search parameters with proper validation and defaults.
    """
    
    query_vector: Embedding = Field(
        ...,
        description="Query vector for similarity search",
        min_items=1,
        max_items=4096
    )
    
    collection: str = Field(
        ...,
        description="Collection to search in",
        min_length=1,
        max_length=255
    )
    
    limit: int = Field(
        default=10,
        description="Maximum number of results to return",
        ge=1,
        le=1000
    )
    
    score_threshold: Optional[float] = Field(
        default=None,
        description="Minimum similarity score threshold",
        ge=0.0,
        le=1.0
    )
    
    include_vectors: bool = Field(
        default=False,
        description="Include vector embeddings in results"
    )
    
    include_metadata: bool = Field(
        default=True,
        description="Include metadata in results"
    )
    
    filter_conditions: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Metadata filter conditions"
    )
    
    @validator('query_vector')
    def validate_query_dimension(cls, v):
        """Validate query vector dimension."""
        if len(v) not in [dim.value for dim in VectorDimension]:
            raise ValueError(f"Unsupported query vector dimension: {len(v)}")
        return v
    
    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "query_vector": [0.1, 0.2, 0.3],
                "collection": "documents",
                "limit": 10,
                "score_threshold": 0.7,
                "include_vectors": False,
                "include_metadata": True,
                "filter_conditions": {"category": "document"}
            }
        }


class VectorSearchResult(BaseModel):
    """
    Vector search result model.
    
    Encapsulates search results with metadata and performance metrics.
    """
    
    vectors: List[Vector] = Field(
        default_factory=list,
        description="List of matching vectors"
    )
    
    total_count: int = Field(
        default=0,
        description="Total number of results found",
        ge=0
    )
    
    query_time_ms: float = Field(
        default=0.0,
        description="Query execution time in milliseconds",
        ge=0.0
    )
    
    collection: str = Field(
        ...,
        description="Collection that was searched"
    )
    
    search_params: VectorSearchRequest = Field(
        ...,
        description="Original search parameters"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Search execution timestamp"
    )
    
    def get_top_score(self) -> Optional[float]:
        """Get the highest similarity score from results."""
        if not self.vectors:
            return None
        return max(v.score for v in self.vectors if v.score is not None)
    
    def get_average_score(self) -> Optional[float]:
        """Get average similarity score from results."""
        if not self.vectors:
            return None
        
        scores = [v.score for v in self.vectors if v.score is not None]
        if not scores:
            return None
        
        return sum(scores) / len(scores)
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class EmbeddingRequest(BaseModel):
    """
    Embedding generation request model.
    
    Encapsulates text-to-embedding conversion parameters.
    """
    
    text: Union[str, List[str]] = Field(
        ...,
        description="Text or list of texts to embed"
    )
    
    model_name: str = Field(
        ...,
        description="Model name for embedding generation",
        min_length=1,
        max_length=255
    )
    
    normalize: bool = Field(
        default=True,
        description="Whether to normalize embeddings"
    )
    
    batch_size: int = Field(
        default=32,
        description="Batch size for processing multiple texts",
        ge=1,
        le=1000
    )
    
    max_length: Optional[int] = Field(
        default=512,
        description="Maximum text length for tokenization",
        ge=1,
        le=8192
    )
    
    @validator('text')
    def validate_text_input(cls, v):
        """Validate text input."""
        if isinstance(v, str):
            if not v.strip():
                raise ValueError("Text cannot be empty")
        elif isinstance(v, list):
            if not v:
                raise ValueError("Text list cannot be empty")
            for text in v:
                if not isinstance(text, str) or not text.strip():
                    raise ValueError("All texts must be non-empty strings")
        else:
            raise ValueError("Text must be string or list of strings")
        return v
    
    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "text": "This is a sample text to embed",
                "model_name": "all-MiniLM-L6-v2",
                "normalize": True,
                "batch_size": 32,
                "max_length": 512
            }
        }


class EmbeddingResponse(BaseModel):
    """
    Embedding generation response model.
    
    Encapsulates embedding results with metadata and performance metrics.
    """
    
    embeddings: List[Embedding] = Field(
        ...,
        description="Generated embeddings"
    )
    
    model_name: str = Field(
        ...,
        description="Model used for embedding generation"
    )
    
    dimension: int = Field(
        ...,
        description="Embedding dimension",
        ge=1,
        le=4096
    )
    
    processing_time_ms: float = Field(
        default=0.0,
        description="Processing time in milliseconds",
        ge=0.0
    )
    
    token_count: Optional[int] = Field(
        default=None,
        description="Total number of tokens processed",
        ge=0
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Processing timestamp"
    )
    
    @validator('embeddings')
    def validate_embeddings(cls, v):
        """Validate embeddings structure."""
        if not v:
            raise ValueError("Embeddings list cannot be empty")
        
        # Check dimension consistency
        if len(set(len(emb) for emb in v)) > 1:
            raise ValueError("All embeddings must have the same dimension")
        
        return v
    
    def get_embedding_count(self) -> int:
        """Get number of embeddings generated."""
        return len(self.embeddings)
    
    def get_average_processing_time(self) -> float:
        """Get average processing time per embedding."""
        if not self.embeddings:
            return 0.0
        return self.processing_time_ms / len(self.embeddings)
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CollectionInfo(BaseModel):
    """
    Collection information model.
    
    Encapsulates collection metadata and statistics.
    """
    
    name: str = Field(
        ...,
        description="Collection name",
        min_length=1,
        max_length=255
    )
    
    dimension: int = Field(
        ...,
        description="Vector dimension for this collection",
        ge=1,
        le=4096
    )
    
    vector_count: int = Field(
        default=0,
        description="Number of vectors in collection",
        ge=0
    )
    
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Collection creation timestamp"
    )
    
    updated_at: Optional[datetime] = Field(
        None,
        description="Last update timestamp"
    )
    
    metadata: Optional[Metadata] = Field(
        default_factory=dict,
        description="Collection metadata"
    )
    
    config: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Collection configuration"
    )
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "name": "documents",
                "dimension": 384,
                "vector_count": 1000,
                "metadata": {"description": "Document embeddings"},
                "config": {"distance": "cosine"}
            }
        }
