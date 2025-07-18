"""
Validation Utilities
===================

Validation utilities for the HANA-X Vector Database Shared Library.
Provides comprehensive validation for vectors, collections, search queries, and batch operations.
"""

import re
from typing import List, Dict, Any, Optional, Union, Tuple
import numpy as np
from .exceptions import (
    ValidationError,
    VectorValidationError,
    SearchValidationError,
    CollectionError
)


class VectorValidator:
    """
    Vector validation utilities.
    Validates vector data, dimensions, and formats.
    """
    
    @staticmethod
    def validate_vector(vector: Union[List[float], np.ndarray], 
                       expected_dimension: Optional[int] = None) -> List[float]:
        """
        Validate vector data.
        
        Args:
            vector: Vector data
            expected_dimension: Expected vector dimension
            
        Returns:
            Validated vector as list
            
        Raises:
            VectorValidationError: If validation fails
        """
        if vector is None:
            raise VectorValidationError("Vector cannot be None")
        
        # Convert to list if numpy array
        if isinstance(vector, np.ndarray):
            if vector.ndim != 1:
                raise VectorValidationError(
                    f"Vector must be 1-dimensional, got {vector.ndim} dimensions"
                )
            vector = vector.tolist()
        
        if not isinstance(vector, list):
            raise VectorValidationError("Vector must be a list or numpy array")
        
        if len(vector) == 0:
            raise VectorValidationError("Vector cannot be empty")
        
        # Validate all elements are numeric
        validated_vector = []
        for i, value in enumerate(vector):
            if not isinstance(value, (int, float)):
                try:
                    value = float(value)
                except (ValueError, TypeError):
                    raise VectorValidationError(
                        f"Vector element at index {i} must be numeric, got {type(value).__name__}"
                    )
            
            if not np.isfinite(value):
                raise VectorValidationError(
                    f"Vector element at index {i} must be finite, got {value}"
                )
            
            validated_vector.append(float(value))
        
        # Validate dimension
        if expected_dimension is not None:
            if len(validated_vector) != expected_dimension:
                raise VectorValidationError(
                    f"Vector dimension mismatch: expected {expected_dimension}, got {len(validated_vector)}",
                    vector_dimension=len(validated_vector),
                    expected_dimension=expected_dimension
                )
        
        return validated_vector
    
    @staticmethod
    def validate_batch_vectors(vectors: List[Union[List[float], np.ndarray]], 
                             expected_dimension: Optional[int] = None) -> List[List[float]]:
        """
        Validate batch of vectors.
        
        Args:
            vectors: List of vectors
            expected_dimension: Expected vector dimension
            
        Returns:
            Validated vectors as list of lists
            
        Raises:
            VectorValidationError: If validation fails
        """
        if not isinstance(vectors, list):
            raise VectorValidationError("Vectors must be a list")
        
        if len(vectors) == 0:
            raise VectorValidationError("Vector batch cannot be empty")
        
        validated_vectors = []
        
        # Validate first vector to determine dimension
        first_vector = VectorValidator.validate_vector(vectors[0], expected_dimension)
        validated_vectors.append(first_vector)
        
        dimension = len(first_vector)
        
        # Validate remaining vectors
        for i, vector in enumerate(vectors[1:], 1):
            try:
                validated_vector = VectorValidator.validate_vector(vector, dimension)
                validated_vectors.append(validated_vector)
            except VectorValidationError as e:
                raise VectorValidationError(
                    f"Vector at index {i} validation failed: {e.message}",
                    vector_dimension=e.vector_dimension,
                    expected_dimension=dimension
                )
        
        return validated_vectors


class CollectionValidator:
    """
    Collection validation utilities.
    Validates collection names, configurations, and parameters.
    """
    
    @staticmethod
    def validate_collection_name(name: str) -> str:
        """
        Validate collection name.
        
        Args:
            name: Collection name
            
        Returns:
            Validated collection name
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(name, str):
            raise ValidationError("Collection name must be a string")
        
        name = name.strip()
        
        if not name:
            raise ValidationError("Collection name cannot be empty")
        
        # Length validation
        if len(name) < 1 or len(name) > 255:
            raise ValidationError("Collection name must be between 1 and 255 characters")
        
        # Character validation (alphanumeric, underscore, hyphen)
        if not re.match(r'^[a-zA-Z0-9_-]+$', name):
            raise ValidationError(
                "Collection name can only contain alphanumeric characters, underscores, and hyphens"
            )
        
        # Must start with letter or underscore
        if not re.match(r'^[a-zA-Z_]', name):
            raise ValidationError("Collection name must start with a letter or underscore")
        
        return name


class SearchValidator:
    """
    Search validation utilities.
    Validates search queries, parameters, and filters.
    """
    
    @staticmethod
    def validate_search_query(query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate search query.
        
        Args:
            query: Search query dictionary
            
        Returns:
            Validated search query
            
        Raises:
            SearchValidationError: If validation fails
        """
        if not isinstance(query, dict):
            raise SearchValidationError("Search query must be a dictionary")
        
        validated_query = {}
        
        # Validate vector
        if 'vector' in query:
            validated_query['vector'] = VectorValidator.validate_vector(query['vector'])
        else:
            raise SearchValidationError("Search query must contain a 'vector' field")
        
        # Validate limit
        if 'limit' in query:
            limit = query['limit']
            if not isinstance(limit, int) or limit <= 0:
                raise SearchValidationError("Search limit must be a positive integer")
            if limit > 10000:
                raise SearchValidationError("Search limit cannot exceed 10000")
            validated_query['limit'] = limit
        else:
            validated_query['limit'] = 10  # Default limit
        
        # Validate offset
        if 'offset' in query:
            offset = query['offset']
            if not isinstance(offset, int) or offset < 0:
                raise SearchValidationError("Search offset must be a non-negative integer")
            validated_query['offset'] = offset
        
        # Validate filter
        if 'filter' in query:
            filter_obj = query['filter']
            if not isinstance(filter_obj, dict):
                raise SearchValidationError("Search filter must be a dictionary")
            validated_query['filter'] = filter_obj
        
        # Validate score threshold
        if 'score_threshold' in query:
            threshold = query['score_threshold']
            if not isinstance(threshold, (int, float)):
                raise SearchValidationError("Score threshold must be numeric")
            if not 0 <= threshold <= 1:
                raise SearchValidationError("Score threshold must be between 0 and 1")
            validated_query['score_threshold'] = float(threshold)
        
        return validated_query


class BatchValidator:
    """
    Batch operation validation utilities.
    Validates batch operations, sizes, and parameters.
    """
    
    @staticmethod
    def validate_batch_size(size: int, max_size: int = 10000) -> int:
        """
        Validate batch size.
        
        Args:
            size: Batch size
            max_size: Maximum allowed batch size
            
        Returns:
            Validated batch size
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(size, int):
            raise ValidationError("Batch size must be an integer")
        
        if size <= 0:
            raise ValidationError("Batch size must be positive")
        
        if size > max_size:
            raise ValidationError(f"Batch size cannot exceed {max_size}")
        
        return size
    
    @staticmethod
    def validate_batch_vectors(vectors: List[Dict[str, Any]], 
                             expected_dimension: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Validate batch of vectors with metadata.
        
        Args:
            vectors: List of vector dictionaries
            expected_dimension: Expected vector dimension
            
        Returns:
            Validated vector batch
            
        Raises:
            VectorValidationError: If validation fails
        """
        if not isinstance(vectors, list):
            raise ValidationError("Vectors must be a list")
        
        if len(vectors) == 0:
            raise ValidationError("Vector batch cannot be empty")
        
        validated_vectors = []
        
        for i, vector_data in enumerate(vectors):
            if not isinstance(vector_data, dict):
                raise ValidationError(f"Vector at index {i} must be a dictionary")
            
            if 'vector' not in vector_data:
                raise ValidationError(f"Vector at index {i} missing 'vector' field")
            
            # Validate vector
            validated_vector = VectorValidator.validate_vector(
                vector_data['vector'], expected_dimension
            )
            
            # Create validated vector data
            validated_data = {
                'vector': validated_vector,
                'id': vector_data.get('id', str(i)),
                'payload': vector_data.get('payload', {})
            }
            
            validated_vectors.append(validated_data)
        
        return validated_vectors


class APIValidator:
    """
    API validation utilities.
    Validates API keys, requests, and responses.
    """
    
    @staticmethod
    def validate_api_key(api_key: str, valid_keys: List[str]) -> str:
        """
        Validate API key.
        
        Args:
            api_key: API key to validate
            valid_keys: List of valid API keys
            
        Returns:
            Validated API key
            
        Raises:
            ValidationError: If validation fails
        """
        if not api_key:
            raise ValidationError("API key cannot be empty")
        
        if api_key not in valid_keys:
            raise ValidationError("Invalid API key")
        
        return api_key
    
    @staticmethod
    def validate_request_size(size: int, max_size: int = 1000) -> bool:
        """
        Validate request size.
        
        Args:
            size: Request size
            max_size: Maximum allowed size
            
        Returns:
            True if valid
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(size, int):
            raise ValidationError("Request size must be an integer")
        
        if size < 1:
            raise ValidationError("Request size must be positive")
        
        if size > max_size:
            raise ValidationError(f"Request size cannot exceed {max_size}")
        
        return True


# Convenience functions for backward compatibility and ease of use
def validate_vector_data(vector: Union[List[float], np.ndarray], 
                        expected_dimension: Optional[int] = None) -> List[float]:
    """
    Validate vector data.
    
    Args:
        vector: Vector data
        expected_dimension: Expected vector dimension
        
    Returns:
        Validated vector as list
        
    Raises:
        VectorValidationError: If validation fails
    """
    return VectorValidator.validate_vector(vector, expected_dimension)


def validate_collection_name(name: str) -> str:
    """
    Validate collection name.
    
    Args:
        name: Collection name
        
    Returns:
        Validated collection name
        
    Raises:
        ValidationError: If validation fails
    """
    return CollectionValidator.validate_collection_name(name)


def validate_search_query(query: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate search query.
    
    Args:
        query: Search query dictionary
        
    Returns:
        Validated search query
        
    Raises:
        SearchValidationError: If validation fails
    """
    return SearchValidator.validate_search_query(query)


def validate_batch_vectors(vectors: List[Union[List[float], np.ndarray]], 
                          expected_dimension: Optional[int] = None) -> List[List[float]]:
    """
    Validate batch of vectors.
    
    Args:
        vectors: List of vectors
        expected_dimension: Expected vector dimension
        
    Returns:
        Validated vectors as list of lists
        
    Raises:
        VectorValidationError: If validation fails
    """
    return VectorValidator.validate_batch_vectors(vectors, expected_dimension)


def validate_api_key(api_key: str) -> bool:
    """
    Validate API key format and structure.
    
    Args:
        api_key: API key string to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not api_key or not isinstance(api_key, str):
        return False
    
    # Basic API key validation (length, format)
    if len(api_key) < 16 or len(api_key) > 128:
        return False
    
    # Check for valid characters (alphanumeric, hyphens, underscores)
    import re
    if not re.match(r'^[a-zA-Z0-9_-]+$', api_key):
        return False
    
    return True


def validate_request_data(request_data: Dict[str, Any]) -> bool:
    """
    Validate general request data structure.
    
    Args:
        request_data: Request data dictionary to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(request_data, dict):
        return False
    
    # Check for required fields based on request type
    if 'type' in request_data:
        request_type = request_data.get('type')
        
        if request_type == 'vector':
            try:
                validate_vector_data(request_data)
                return True
            except Exception:
                return False
        elif request_type == 'collection':
            try:
                validate_collection_name(request_data.get('name', ''))
                return True
            except Exception:
                return False
        elif request_type == 'search':
            try:
                validate_search_query(request_data)
                return True
            except Exception:
                return False
    
    # Generic validation for untyped requests
    return True  # Allow generic requests
