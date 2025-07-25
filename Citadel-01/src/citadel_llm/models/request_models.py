from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal, Any

class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str

class ChatCompletionRequest(BaseModel):
    model: str = Field(..., description="The model to use for completion (e.g., 'phi3', 'mixtral').")
    messages: List[ChatMessage] = Field(..., description="A list of messages comprising the conversation.")
    stream: Optional[bool] = False
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None

class GenerateRequest(BaseModel):
    model: str = Field(..., description="The model to use for generation (e.g., 'phi3', 'mixtral').")
    prompt: str = Field(..., description="The input prompt string.")
    stream: Optional[bool] = False
    raw: Optional[bool] = False
    options: Optional[Dict[str, Any]] = {}

class EmbeddingRequest(BaseModel):
    model: str = Field(..., description="The embedding model to use (e.g., 'nomic-embed-text').")
    prompt: str = Field(..., description="The text to generate embedding for.")

class HealthResponse(BaseModel):
    status: str
    services: Dict[str, str]
    version: str
    environment: str

class ModelInfo(BaseModel):
    name: str
    modified_at: str
    size: int
    digest: str

class ModelsResponse(BaseModel):
    models: List[ModelInfo]