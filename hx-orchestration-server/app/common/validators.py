"""
Input validation utilities for the orchestration server.

This module provides validation functions for API inputs to ensure
data integrity and security across all endpoints.
"""

from typing import List, Union
from fastapi import HTTPException


def validate_input_length(texts: List[str], max_length: int = 8192, max_batch_size: int = 100) -> None:
    """
    Validate text input length and batch size constraints.
    
    Args:
        texts: List of text strings to validate
        max_length: Maximum length per text string
        max_batch_size: Maximum number of texts in batch
        
    Raises:
        HTTPException: If validation fails
    """
    if len(texts) > max_batch_size:
        raise HTTPException(
            status_code=400,
            detail=f"Batch size {len(texts)} exceeds maximum {max_batch_size}"
        )
    
    for i, text in enumerate(texts):
        if not isinstance(text, str):
            raise HTTPException(
                status_code=400,
                detail=f"Text at index {i} must be a string"
            )
        
        if len(text) == 0:
            raise HTTPException(
                status_code=400,
                detail=f"Text at index {i} cannot be empty"
            )
            
        if len(text) > max_length:
            raise HTTPException(
                status_code=400,
                detail=f"Text at index {i} exceeds maximum length {max_length}"
            )


def validate_model_name(model: str, available_models: List[str]) -> None:
    """
    Validate that the requested model is available.
    
    Args:
        model: Model name to validate
        available_models: List of available model names
        
    Raises:
        HTTPException: If model is not available
    """
    if model not in available_models:
        raise HTTPException(
            status_code=400,
            detail=f"Model '{model}' not available. Available models: {available_models}"
        )


def validate_llm_request(
    prompt: str, 
    max_tokens: int = None,
    temperature: float = None
) -> None:
    """
    Validate LLM generation request parameters.
    
    Args:
        prompt: Input prompt to validate
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature
        
    Raises:
        HTTPException: If validation fails
    """
    if not isinstance(prompt, str) or len(prompt.strip()) == 0:
        raise HTTPException(
            status_code=400,
            detail="Prompt must be a non-empty string"
        )
    
    if len(prompt) > 32768:  # 32K character limit
        raise HTTPException(
            status_code=400,
            detail="Prompt exceeds maximum length of 32,768 characters"
        )
    
    if max_tokens is not None:
        if not isinstance(max_tokens, int) or max_tokens <= 0:
            raise HTTPException(
                status_code=400,
                detail="max_tokens must be a positive integer"
            )
        
        if max_tokens > 4096:  # Reasonable limit
            raise HTTPException(
                status_code=400,
                detail="max_tokens cannot exceed 4096"
            )
    
    if temperature is not None:
        if not isinstance(temperature, (int, float)):
            raise HTTPException(
                status_code=400,
                detail="temperature must be a number"
            )
        
        if temperature < 0.0 or temperature > 2.0:
            raise HTTPException(
                status_code=400,
                detail="temperature must be between 0.0 and 2.0"
            )


def sanitize_user_input(text: str) -> str:
    """
    Sanitize user input to prevent injection attacks.
    
    Args:
        text: Raw user input
        
    Returns:
        str: Sanitized text
    """
    # Basic sanitization - remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', '\x00', '\r']
    
    sanitized = text
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    # Normalize whitespace
    sanitized = ' '.join(sanitized.split())
    
    return sanitized.strip()
