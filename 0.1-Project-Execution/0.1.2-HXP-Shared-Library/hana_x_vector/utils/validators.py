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
        
        # Validate type
        if not isinstance(vector, list):
            raise VectorValidationError(
                f"Vector must be a list or numpy array, got {type(vector)}"
            )
        
        # Validate not empty
        if len(vector) == 0:
            raise VectorValidationError("Vector cannot be empty")
        
        # Validate dimension
        if expected_dimension is not None and len(vector) != expected_dimension:
            raise VectorValidationError(
                f"Vector dimension mismatch: expected {expected_dimension}, got {len(vector)}",
                vector_dimension=len(vector),
                expected_dimension=expected_dimension
            )
        
        # Validate all elements are numbers
        validated_vector = []
        for i, value in enumerate(vector):
            if not isinstance(value, (int, float)):
                try:
                    value = float(value)
                except (ValueError, TypeError):
                    raise VectorValidationError(
                        f"Vector element at index {i} is not a valid number: {value}"
                    )
            
            # Check for NaN and infinity
            if np.isnan(value):
                raise VectorValidationError(f"Vector element at index {i} is NaN")
            
            if np.isinf(value):
                raise VectorValidationError(f"Vector element at index {i} is infinite")
            
            validated_vector.append(float(value))
        
        return validated_vector
    
    @staticmethod
    def validate_vector_batch(vectors: List[Union[List[float], np.ndarray]], 
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
    
    @staticmethod
    def validate_vector_id(vector_id: Any) -> str:
        """
        Validate vector ID.
        
        Args:
            vector_id: Vector ID
            
        Returns:
            Validated vector ID as string
            
        Raises:
            ValidationError: If validation fails
        """
        if vector_id is None:
            raise ValidationError("Vector ID cannot be None")
        
        # Convert to string
        vector_id_str = str(vector_id)
        
        # Validate not empty
        if not vector_id_str.strip():
            raise ValidationError("Vector ID cannot be empty")
        
        # Validate length
        if len(vector_id_str) > 255:
            raise ValidationError("Vector ID cannot exceed 255 characters")
        
        return vector_id_str.strip()
    
    @staticmethod
    def validate_payload(payload: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Validate vector payload.
        
        Args:
            payload: Vector payload
            
        Returns:
            Validated payload
            
        Raises:
            ValidationError: If validation fails
        """
        if payload is None:
            return None
        
        if not isinstance(payload, dict):
            raise ValidationError("Payload must be a dictionary")
        
        # Validate payload size (approximate)
        payload_str = str(payload)
        if len(payload_str) > 1024 * 1024:  # 1MB limit
            raise ValidationError("Payload size exceeds 1MB limit")
        
        # Validate keys
        for key in payload.keys():
            if not isinstance(key, str):
                raise ValidationError(f"Payload key must be string, got {type(key)}")
            
            if not key.strip():
                raise ValidationError("Payload key cannot be empty")
        
        return payload


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
    
    @staticmethod
    def validate_vector_size(size: int) -> int:
        """
        Validate vector size.
        
        Args:
            size: Vector size
            
        Returns:
            Validated vector size
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(size, int):
            raise ValidationError("Vector size must be an integer")
        
        if size <= 0:
            raise ValidationError("Vector size must be positive")
        
        if size > 65536:  # 64K limit
            raise ValidationError("Vector size cannot exceed 65536")
        
        return size
    
    @staticmethod
    def validate_distance_metric(metric: str) -> str:
        """
        Validate distance metric.
        
        Args:
            metric: Distance metric
            
        Returns:
            Validated distance metric
            
        Raises:
            ValidationError: If validation fails
        """
        valid_metrics = ["cosine", "euclidean", "dot", "manhattan"]
        
        if not isinstance(metric, str):
            raise ValidationError("Distance metric must be a string")
        
        metric = metric.lower().strip()
        
        if metric not in valid_metrics:
            raise ValidationError(
                f"Invalid distance metric: {metric}. Valid options: {valid_metrics}"
            )
        
        return metric
    
    @staticmethod
    def validate_collection_config(config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate collection configuration.
        
        Args:
            config: Collection configuration
            
        Returns:
            Validated configuration
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(config, dict):
            raise ValidationError("Collection config must be a dictionary")
        
        validated_config = {}
        
        # Validate vector size
        if "vector_size" in config:
            validated_config["vector_size"] = CollectionValidator.validate_vector_size(
                config["vector_size"]
            )
        
        # Validate distance metric
        if "distance" in config:
            validated_config["distance"] = CollectionValidator.validate_distance_metric(
                config["distance"]
            )
        
        # Validate shard number
        if "shard_number" in config:
            shard_number = config["shard_number"]
            if not isinstance(shard_number, int) or shard_number <= 0:
                raise ValidationError("Shard number must be a positive integer")
            validated_config["shard_number"] = shard_number
        
        # Validate replication factor
        if "replication_factor" in config:
            replication_factor = config["replication_factor"]
            if not isinstance(replication_factor, int) or replication_factor <= 0:
                raise ValidationError("Replication factor must be a positive integer")
            validated_config["replication_factor"] = replication_factor
        
        # Copy other valid fields
        for key, value in config.items():
            if key not in validated_config:
                validated_config[key] = value
        
        return validated_config


class SearchValidator:
    """
    Search validation utilities.
    Validates search queries, parameters, and filters.
    """
    
    @staticmethod
    def validate_search_vector(vector: Union[List[float], np.ndarray], 
                             expected_dimension: Optional[int] = None) -> List[float]:
        """
        Validate search vector.
        
        Args:
            vector: Search vector
            expected_dimension: Expected vector dimension
            
        Returns:
            Validated search vector
            
        Raises:
            SearchValidationError: If validation fails
        """
        try:
            return VectorValidator.validate_vector(vector, expected_dimension)
        except VectorValidationError as e:
            raise SearchValidationError(f"Search vector validation failed: {e.message}")
    
    @staticmethod
    def validate_search_limit(limit: int) -> int:
        """
        Validate search limit.
        
        Args:
            limit: Search limit
            
        Returns:
            Validated search limit
            
        Raises:
            SearchValidationError: If validation fails
        """
        if not isinstance(limit, int):
            raise SearchValidationError("Search limit must be an integer")
        
        if limit <= 0:
            raise SearchValidationError("Search limit must be positive")
        
        if limit > 10000:  # 10K limit
            raise SearchValidationError("Search limit cannot exceed 10000")
        
        return limit
    
    @staticmethod
    def validate_search_offset(offset: int) -> int:
        """
        Validate search offset.
        
        Args:
            offset: Search offset
            
        Returns:
            Validated search offset
            
        Raises:
            SearchValidationError: If validation fails
        """
        if not isinstance(offset, int):
            raise SearchValidationError("Search offset must be an integer")
        
        if offset < 0:
            raise SearchValidationError("Search offset cannot be negative")
        
        if offset > 1000000:  # 1M limit
            raise SearchValidationError("Search offset cannot exceed 1000000")
        
        return offset
    
    @staticmethod
    def validate_search_filter(filter_dict: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Validate search filter.
        
        Args:
            filter_dict: Search filter
            
        Returns:
            Validated search filter
            
        Raises:
            SearchValidationError: If validation fails
        """
        if filter_dict is None:
            return None
        
        if not isinstance(filter_dict, dict):
            raise SearchValidationError("Search filter must be a dictionary")
        
        # Basic validation - in production would validate against schema
        validated_filter = {}
        
        for key, value in filter_dict.items():
            if not isinstance(key, str):
                raise SearchValidationError("Filter key must be a string")
            
            if not key.strip():
                raise SearchValidationError("Filter key cannot be empty")
            
            validated_filter[key] = value
        
        return validated_filter
    
    @staticmethod
    def validate_search_params(params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate search parameters.
        
        Args:
            params: Search parameters
            
        Returns:
            Validated search parameters
            
        Raises:
            SearchValidationError: If validation fails
        """
        if not isinstance(params, dict):
            raise SearchValidationError("Search params must be a dictionary")
        
        validated_params = {}
        
        # Validate vector
        if "vector" in params:
            validated_params["vector"] = SearchValidator.validate_search_vector(
                params["vector"]
            )
        
        # Validate limit
        if "limit" in params:
            validated_params["limit"] = SearchValidator.validate_search_limit(
                params["limit"]
            )
        
        # Validate offset
        if "offset" in params:
            validated_params["offset"] = SearchValidator.validate_search_offset(
                params["offset"]
            )
        
        # Validate filter
        if "filter" in params:
            validated_params["filter"] = SearchValidator.validate_search_filter(
                params["filter"]
            )
        
        # Validate score threshold
        if "score_threshold" in params:
            threshold = params["score_threshold"]
            if not isinstance(threshold, (int, float)):
                raise SearchValidationError("Score threshold must be a number")
            
            if threshold < 0 or threshold > 1:
                raise SearchValidationError("Score threshold must be between 0 and 1")
            
            validated_params["score_threshold"] = float(threshold)
        
        # Copy other valid fields
        for key, value in params.items():
            if key not in validated_params:
                validated_params[key] = value
        
        return validated_params


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
            ValidationError: If validation fails
        """
        if not isinstance(vectors, list):
            raise ValidationError("Batch vectors must be a list")
        
        if len(vectors) == 0:
            raise ValidationError("Batch vectors cannot be empty")
        
        validated_vectors = []
        
        for i, vector_data in enumerate(vectors):
            if not isinstance(vector_data, dict):
                raise ValidationError(f"Vector at index {i} must be a dictionary")
            
            validated_vector = {}
            
            # Validate ID
            if "id" in vector_data:
                validated_vector["id"] = VectorValidator.validate_vector_id(
                    vector_data["id"]
                )
            
            # Validate vector
            if "vector" in vector_data:
                validated_vector["vector"] = VectorValidator.validate_vector(
                    vector_data["vector"], expected_dimension
                )
            else:
                raise ValidationError(f"Vector at index {i} missing 'vector' field")
            
            # Validate payload
            if "payload" in vector_data:
                validated_vector["payload"] = VectorValidator.validate_payload(
                    vector_data["payload"]
                )
            
            # Copy other fields
            for key, value in vector_data.items():
                if key not in validated_vector:
                    validated_vector[key] = value
            
            validated_vectors.append(validated_vector)
        
        return validated_vectors
    
    @staticmethod
    def validate_batch_operation(operation: str, data: Any) -> Tuple[str, Any]:
        """
        Validate batch operation.
        
        Args:
            operation: Operation type
            data: Operation data
            
        Returns:
            Validated operation and data
            
        Raises:
            ValidationError: If validation fails
        """
        valid_operations = ["insert", "update", "delete", "upsert"]
        
        if not isinstance(operation, str):
            raise ValidationError("Operation must be a string")
        
        operation = operation.lower().strip()
        
        if operation not in valid_operations:
            raise ValidationError(
                f"Invalid operation: {operation}. Valid options: {valid_operations}"
            )
        
        # Validate data based on operation
        if operation in ["insert", "update", "upsert"]:
            if not isinstance(data, list):
                raise ValidationError(f"Data for {operation} must be a list")
            
            validated_data = BatchValidator.validate_batch_vectors(data)
        
        elif operation == "delete":
            if not isinstance(data, list):
                raise ValidationError("Data for delete must be a list")
            
            validated_data = []
            for i, item in enumerate(data):
                if isinstance(item, dict) and "id" in item:
                    validated_data.append({
                        "id": VectorValidator.validate_vector_id(item["id"])
                    })
                else:
                    validated_data.append({
                        "id": VectorValidator.validate_vector_id(item)
                    })
        
        else:
            validated_data = data
        
        return operation, validated_data
    
    @staticmethod
    def validate_parallel_config(config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate parallel processing configuration.
        
        Args:
            config: Parallel configuration
            
        Returns:
            Validated configuration
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(config, dict):
            raise ValidationError("Parallel config must be a dictionary")
        
        validated_config = {}
        
        # Validate max workers
        if "max_workers" in config:
            max_workers = config["max_workers"]
            if not isinstance(max_workers, int) or max_workers <= 0:
                raise ValidationError("Max workers must be a positive integer")
            
            if max_workers > 100:
                raise ValidationError("Max workers cannot exceed 100")
            
            validated_config["max_workers"] = max_workers
        
        # Validate chunk size
        if "chunk_size" in config:
            chunk_size = config["chunk_size"]
            if not isinstance(chunk_size, int) or chunk_size <= 0:
                raise ValidationError("Chunk size must be a positive integer")
            
            validated_config["chunk_size"] = chunk_size
        
        # Validate timeout
        if "timeout" in config:
            timeout = config["timeout"]
            if not isinstance(timeout, (int, float)) or timeout <= 0:
                raise ValidationError("Timeout must be a positive number")
            
            validated_config["timeout"] = float(timeout)
        
        # Copy other valid fields
        for key, value in config.items():
            if key not in validated_config:
                validated_config[key] = value
        
        return validated_config


class RequestValidator:
    """
    Request validation utilities.
    Validates API requests and parameters.
    """
    
    @staticmethod
    def validate_request_size(data: Any, max_size: int = 10 * 1024 * 1024) -> Any:
        """
        Validate request size.
        
        Args:
            data: Request data
            max_size: Maximum size in bytes
            
        Returns:
            Validated data
            
        Raises:
            ValidationError: If validation fails
        """
        # Approximate size calculation
        data_str = str(data)
        size = len(data_str.encode('utf-8'))
        
        if size > max_size:
            raise ValidationError(f"Request size {size} exceeds limit {max_size}")
        
        return data
    
    @staticmethod
    def validate_pagination(offset: int, limit: int) -> Tuple[int, int]:
        """
        Validate pagination parameters.
        
        Args:
            offset: Pagination offset
            limit: Pagination limit
            
        Returns:
            Validated offset and limit
            
        Raises:
            ValidationError: If validation fails
        """
        validated_offset = SearchValidator.validate_search_offset(offset)
        validated_limit = SearchValidator.validate_search_limit(limit)
        
        return validated_offset, validated_limit
    
    @staticmethod
    def validate_api_key(api_key: Optional[str], valid_keys: List[str]) -> str:
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
            raise ValidationError("API key is required")
        
        if not isinstance(api_key, str):
            raise ValidationError("API key must be a string")
        
        api_key = api_key.strip()
        
        if not api_key:
            raise ValidationError("API key cannot be empty")
        
        if api_key not in valid_keys:
            raise ValidationError("Invalid API key")
        
        return api_key
    
    @staticmethod
    def validate_content_type(content_type: Optional[str], 
                            allowed_types: List[str]) -> str:
        """
        Validate content type.
        
        Args:
            content_type: Content type header
            allowed_types: List of allowed content types
            
        Returns:
            Validated content type
            
        Raises:
            ValidationError: If validation fails
        """
        if not content_type:
            raise ValidationError("Content-Type header is required")
        
        content_type = content_type.lower().strip()
        
        # Extract main type (ignore charset, etc.)
        main_type = content_type.split(';')[0].strip()
        
        if main_type not in allowed_types:
            raise ValidationError(
                f"Invalid content type: {main_type}. Allowed: {allowed_types}"
            )
        
        return main_type
