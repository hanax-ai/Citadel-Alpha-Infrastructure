"""
Custom Exceptions
================

Custom exception classes for the HANA-X Vector Database Shared Library.
Provides specific error types for different components and operations.
"""

from typing import Optional, Dict, Any


class VectorDatabaseError(Exception):
    """Base exception for vector database operations."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details
        }


class QdrantError(VectorDatabaseError):
    """Exception for Qdrant-related errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, 
                 operation: Optional[str] = None, collection: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.status_code = status_code
        self.operation = operation
        self.collection = collection
        
        # Add operation-specific details
        if operation:
            self.details["operation"] = operation
        if collection:
            self.details["collection"] = collection
        if status_code:
            self.details["status_code"] = status_code


class QdrantConnectionError(QdrantError):
    """Exception for Qdrant connection errors."""
    
    def __init__(self, message: str, host: Optional[str] = None, port: Optional[int] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.host = host
        self.port = port
        
        if host:
            self.details["host"] = host
        if port:
            self.details["port"] = port


class QdrantTimeoutError(QdrantError):
    """Exception for Qdrant timeout errors."""
    
    def __init__(self, message: str, timeout: Optional[float] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.timeout = timeout
        
        if timeout:
            self.details["timeout"] = timeout


class CollectionError(QdrantError):
    """Exception for collection-related errors."""
    
    def __init__(self, message: str, collection_name: str, **kwargs):
        super().__init__(message, collection=collection_name, **kwargs)
        self.collection_name = collection_name


class CollectionNotFoundError(CollectionError):
    """Exception for collection not found errors."""
    pass


class CollectionAlreadyExistsError(CollectionError):
    """Exception for collection already exists errors."""
    pass


class VectorOperationError(VectorDatabaseError):
    """Exception for vector operation errors."""
    
    def __init__(self, message: str, operation: str, vector_count: Optional[int] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.operation = operation
        self.vector_count = vector_count
        
        self.details["operation"] = operation
        if vector_count is not None:
            self.details["vector_count"] = vector_count


class VectorInsertError(VectorOperationError):
    """Exception for vector insert errors."""
    
    def __init__(self, message: str, vector_count: Optional[int] = None, **kwargs):
        super().__init__(message, "insert", vector_count, **kwargs)


class VectorSearchError(VectorOperationError):
    """Exception for vector search errors."""
    
    def __init__(self, message: str, query_vector_size: Optional[int] = None, 
                 limit: Optional[int] = None, **kwargs):
        super().__init__(message, "search", **kwargs)
        self.query_vector_size = query_vector_size
        self.limit = limit
        
        if query_vector_size is not None:
            self.details["query_vector_size"] = query_vector_size
        if limit is not None:
            self.details["limit"] = limit


class VectorUpdateError(VectorOperationError):
    """Exception for vector update errors."""
    
    def __init__(self, message: str, vector_count: Optional[int] = None, **kwargs):
        super().__init__(message, "update", vector_count, **kwargs)


class VectorDeleteError(VectorOperationError):
    """Exception for vector delete errors."""
    
    def __init__(self, message: str, vector_count: Optional[int] = None, **kwargs):
        super().__init__(message, "delete", vector_count, **kwargs)


class BatchOperationError(VectorOperationError):
    """Exception for batch operation errors."""
    
    def __init__(self, message: str, operation: str, batch_size: int, 
                 failed_count: Optional[int] = None, **kwargs):
        super().__init__(message, operation, batch_size, **kwargs)
        self.batch_size = batch_size
        self.failed_count = failed_count
        
        self.details["batch_size"] = batch_size
        if failed_count is not None:
            self.details["failed_count"] = failed_count


class CacheError(VectorDatabaseError):
    """Exception for cache-related errors."""
    
    def __init__(self, message: str, cache_type: Optional[str] = None, 
                 key: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.cache_type = cache_type
        self.key = key
        
        if cache_type:
            self.details["cache_type"] = cache_type
        if key:
            self.details["key"] = key


class CacheConnectionError(CacheError):
    """Exception for cache connection errors."""
    
    def __init__(self, message: str, host: Optional[str] = None, port: Optional[int] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.host = host
        self.port = port
        
        if host:
            self.details["host"] = host
        if port:
            self.details["port"] = port


class CacheTimeoutError(CacheError):
    """Exception for cache timeout errors."""
    
    def __init__(self, message: str, timeout: Optional[float] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.timeout = timeout
        
        if timeout:
            self.details["timeout"] = timeout


class ValidationError(VectorDatabaseError):
    """Exception for validation errors."""
    
    def __init__(self, message: str, field: Optional[str] = None, 
                 value: Optional[Any] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.field = field
        self.value = value
        
        if field:
            self.details["field"] = field
        if value is not None:
            self.details["value"] = str(value)


class VectorValidationError(ValidationError):
    """Exception for vector validation errors."""
    
    def __init__(self, message: str, vector_dimension: Optional[int] = None, 
                 expected_dimension: Optional[int] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.vector_dimension = vector_dimension
        self.expected_dimension = expected_dimension
        
        if vector_dimension is not None:
            self.details["vector_dimension"] = vector_dimension
        if expected_dimension is not None:
            self.details["expected_dimension"] = expected_dimension


class SearchValidationError(ValidationError):
    """Exception for search validation errors."""
    
    def __init__(self, message: str, query_type: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.query_type = query_type
        
        if query_type:
            self.details["query_type"] = query_type


class ExternalModelError(VectorDatabaseError):
    """Exception for external model errors."""
    
    def __init__(self, message: str, model_name: Optional[str] = None, 
                 server: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.model_name = model_name
        self.server = server
        
        if model_name:
            self.details["model_name"] = model_name
        if server:
            self.details["server"] = server


class ExternalModelConnectionError(ExternalModelError):
    """Exception for external model connection errors."""
    
    def __init__(self, message: str, model_name: str, server: str, **kwargs):
        super().__init__(message, model_name, server, **kwargs)


class ExternalModelTimeoutError(ExternalModelError):
    """Exception for external model timeout errors."""
    
    def __init__(self, message: str, model_name: str, timeout: float, **kwargs):
        super().__init__(message, model_name, **kwargs)
        self.timeout = timeout
        self.details["timeout"] = timeout


class ExternalModelResponseError(ExternalModelError):
    """Exception for external model response errors."""
    
    def __init__(self, message: str, model_name: str, status_code: Optional[int] = None, 
                 response_text: Optional[str] = None, **kwargs):
        super().__init__(message, model_name, **kwargs)
        self.status_code = status_code
        self.response_text = response_text
        
        if status_code:
            self.details["status_code"] = status_code
        if response_text:
            self.details["response_text"] = response_text


class AuthenticationError(VectorDatabaseError):
    """Exception for authentication errors."""
    
    def __init__(self, message: str, auth_type: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.auth_type = auth_type
        
        if auth_type:
            self.details["auth_type"] = auth_type


class AuthorizationError(VectorDatabaseError):
    """Exception for authorization errors."""
    
    def __init__(self, message: str, resource: Optional[str] = None, 
                 action: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.resource = resource
        self.action = action
        
        if resource:
            self.details["resource"] = resource
        if action:
            self.details["action"] = action


class RateLimitError(VectorDatabaseError):
    """Exception for rate limiting errors."""
    
    def __init__(self, message: str, limit: Optional[int] = None, 
                 window: Optional[int] = None, retry_after: Optional[int] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.limit = limit
        self.window = window
        self.retry_after = retry_after
        
        if limit:
            self.details["limit"] = limit
        if window:
            self.details["window"] = window
        if retry_after:
            self.details["retry_after"] = retry_after


class APIGatewayError(VectorDatabaseError):
    """Exception for API Gateway errors."""
    
    def __init__(self, message: str, endpoint: Optional[str] = None, 
                 method: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.endpoint = endpoint
        self.method = method
        
        if endpoint:
            self.details["endpoint"] = endpoint
        if method:
            self.details["method"] = method


class MiddlewareError(APIGatewayError):
    """Exception for middleware errors."""
    
    def __init__(self, message: str, middleware_name: str, **kwargs):
        super().__init__(message, **kwargs)
        self.middleware_name = middleware_name
        self.details["middleware_name"] = middleware_name


class HealthCheckError(VectorDatabaseError):
    """Exception for health check errors."""
    
    def __init__(self, message: str, check_name: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.check_name = check_name
        
        if check_name:
            self.details["check_name"] = check_name


class MonitoringError(VectorDatabaseError):
    """Exception for monitoring errors."""
    
    def __init__(self, message: str, component: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.component = component
        
        if component:
            self.details["component"] = component


class MetricsError(MonitoringError):
    """Exception for metrics collection errors."""
    
    def __init__(self, message: str, metric_name: Optional[str] = None, **kwargs):
        super().__init__(message, "metrics", **kwargs)
        self.metric_name = metric_name
        
        if metric_name:
            self.details["metric_name"] = metric_name


class ConfigurationError(VectorDatabaseError):
    """Exception for configuration errors."""
    
    def __init__(self, message: str, config_section: Optional[str] = None, 
                 config_key: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.config_section = config_section
        self.config_key = config_key
        
        if config_section:
            self.details["config_section"] = config_section
        if config_key:
            self.details["config_key"] = config_key


class RetryExhaustedError(VectorDatabaseError):
    """Exception for retry exhaustion errors."""
    
    def __init__(self, message: str, operation: str, attempts: int, 
                 last_error: Optional[Exception] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.operation = operation
        self.attempts = attempts
        self.last_error = last_error
        
        self.details["operation"] = operation
        self.details["attempts"] = attempts
        if last_error:
            self.details["last_error"] = str(last_error)


class CircuitBreakerError(VectorDatabaseError):
    """Exception for circuit breaker errors."""
    
    def __init__(self, message: str, service: str, failure_count: int, **kwargs):
        super().__init__(message, **kwargs)
        self.service = service
        self.failure_count = failure_count
        
        self.details["service"] = service
        self.details["failure_count"] = failure_count


class ResourceExhaustedError(VectorDatabaseError):
    """Exception for resource exhaustion errors."""
    
    def __init__(self, message: str, resource_type: str, limit: Optional[int] = None, 
                 current: Optional[int] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.resource_type = resource_type
        self.limit = limit
        self.current = current
        
        self.details["resource_type"] = resource_type
        if limit is not None:
            self.details["limit"] = limit
        if current is not None:
            self.details["current"] = current


class DataIntegrityError(VectorDatabaseError):
    """Exception for data integrity errors."""
    
    def __init__(self, message: str, data_type: Optional[str] = None, 
                 corruption_type: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.data_type = data_type
        self.corruption_type = corruption_type
        
        if data_type:
            self.details["data_type"] = data_type
        if corruption_type:
            self.details["corruption_type"] = corruption_type


class SerializationError(VectorDatabaseError):
    """Exception for serialization/deserialization errors."""
    
    def __init__(self, message: str, data_format: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.data_format = data_format
        
        if data_format:
            self.details["data_format"] = data_format


# Exception mapping for HTTP status codes
HTTP_STATUS_EXCEPTIONS = {
    400: ValidationError,
    401: AuthenticationError,
    403: AuthorizationError,
    404: CollectionNotFoundError,
    409: CollectionAlreadyExistsError,
    429: RateLimitError,
    500: VectorDatabaseError,
    502: ExternalModelConnectionError,
    503: ResourceExhaustedError,
    504: QdrantTimeoutError
}


def create_exception_from_status(status_code: int, message: str, **kwargs) -> VectorDatabaseError:
    """
    Create appropriate exception from HTTP status code.
    
    Args:
        status_code: HTTP status code
        message: Error message
        **kwargs: Additional exception parameters
        
    Returns:
        Appropriate exception instance
    """
    exception_class = HTTP_STATUS_EXCEPTIONS.get(status_code, VectorDatabaseError)
    return exception_class(message, **kwargs)


def handle_qdrant_error(error: Exception, operation: str, collection: Optional[str] = None) -> QdrantError:
    """
    Convert generic error to QdrantError.
    
    Args:
        error: Original error
        operation: Operation that failed
        collection: Collection name if applicable
        
    Returns:
        QdrantError instance
    """
    if isinstance(error, QdrantError):
        return error
    
    message = f"Qdrant {operation} failed: {str(error)}"
    
    # Check for specific error types
    if "timeout" in str(error).lower():
        return QdrantTimeoutError(message, operation=operation, collection=collection)
    elif "connection" in str(error).lower():
        return QdrantConnectionError(message, operation=operation, collection=collection)
    else:
        return QdrantError(message, operation=operation, collection=collection)


def handle_cache_error(error: Exception, operation: str, key: Optional[str] = None) -> CacheError:
    """
    Convert generic error to CacheError.
    
    Args:
        error: Original error
        operation: Operation that failed
        key: Cache key if applicable
        
    Returns:
        CacheError instance
    """
    if isinstance(error, CacheError):
        return error
    
    message = f"Cache {operation} failed: {str(error)}"
    
    # Check for specific error types
    if "timeout" in str(error).lower():
        return CacheTimeoutError(message, key=key)
    elif "connection" in str(error).lower():
        return CacheConnectionError(message, key=key)
    else:
        return CacheError(message, cache_type="redis", key=key)


def handle_external_model_error(error: Exception, model_name: str, operation: str) -> ExternalModelError:
    """
    Convert generic error to ExternalModelError.
    
    Args:
        error: Original error
        model_name: Model name
        operation: Operation that failed
        
    Returns:
        ExternalModelError instance
    """
    if isinstance(error, ExternalModelError):
        return error
    
    message = f"External model {operation} failed for {model_name}: {str(error)}"
    
    # Check for specific error types
    if "timeout" in str(error).lower():
        return ExternalModelTimeoutError(message, model_name)
    elif "connection" in str(error).lower():
        return ExternalModelConnectionError(message, model_name, "unknown")
    else:
        return ExternalModelError(message, model_name)
