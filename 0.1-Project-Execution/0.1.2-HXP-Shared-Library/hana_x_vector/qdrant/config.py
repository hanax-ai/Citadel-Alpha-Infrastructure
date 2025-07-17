"""
Qdrant Configuration Manager
===========================

Configuration management for Qdrant vector database connections and settings.
Handles connection parameters, retry policies, and performance tuning.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from ..utils.exceptions import QdrantError, ValidationError


@dataclass
class QdrantConnectionConfig:
    """Qdrant connection configuration."""
    host: str = "192.168.10.30"
    port: int = 6333
    grpc_port: int = 6334
    timeout: float = 30.0
    api_key: Optional[str] = None
    https: bool = False
    prefix: Optional[str] = None


@dataclass
class QdrantRetryConfig:
    """Qdrant retry configuration."""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True


@dataclass
class QdrantPerformanceConfig:
    """Qdrant performance configuration."""
    batch_size: int = 1000
    max_connections: int = 100
    connection_timeout: float = 10.0
    read_timeout: float = 60.0
    write_timeout: float = 60.0
    pool_size: int = 10
    max_retries_per_request: int = 3


@dataclass
class QdrantCollectionDefaults:
    """Default collection configuration."""
    vector_size: int = 384
    distance: str = "cosine"
    shard_number: int = 1
    replication_factor: int = 1
    write_consistency_factor: int = 1
    on_disk_payload: bool = True
    hnsw_config: Dict[str, Any] = field(default_factory=lambda: {
        "m": 16,
        "ef_construct": 100,
        "full_scan_threshold": 10000
    })


class QdrantConfigManager:
    """
    Qdrant configuration management.
    Handles connection parameters, retry policies, and performance tuning.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._validate_config()
        
        # Parse configuration sections
        self.connection = self._parse_connection_config()
        self.retry = self._parse_retry_config()
        self.performance = self._parse_performance_config()
        self.collection_defaults = self._parse_collection_defaults()
    
    def _validate_config(self):
        """Validate configuration parameters."""
        if not isinstance(self.config, dict):
            raise ValidationError("Qdrant config must be a dictionary")
        
        # Validate connection parameters
        connection_config = self.config.get("connection", {})
        
        if "host" in connection_config:
            if not isinstance(connection_config["host"], str):
                raise ValidationError("Qdrant host must be a string")
        
        if "port" in connection_config:
            port = connection_config["port"]
            if not isinstance(port, int) or port <= 0 or port > 65535:
                raise ValidationError("Qdrant port must be a valid port number")
        
        if "grpc_port" in connection_config:
            grpc_port = connection_config["grpc_port"]
            if not isinstance(grpc_port, int) or grpc_port <= 0 or grpc_port > 65535:
                raise ValidationError("Qdrant gRPC port must be a valid port number")
        
        if "timeout" in connection_config:
            timeout = connection_config["timeout"]
            if not isinstance(timeout, (int, float)) or timeout <= 0:
                raise ValidationError("Qdrant timeout must be a positive number")
        
        # Validate retry parameters
        retry_config = self.config.get("retry", {})
        
        if "max_attempts" in retry_config:
            max_attempts = retry_config["max_attempts"]
            if not isinstance(max_attempts, int) or max_attempts <= 0:
                raise ValidationError("Max retry attempts must be a positive integer")
        
        if "base_delay" in retry_config:
            base_delay = retry_config["base_delay"]
            if not isinstance(base_delay, (int, float)) or base_delay < 0:
                raise ValidationError("Base retry delay must be non-negative")
        
        # Validate performance parameters
        performance_config = self.config.get("performance", {})
        
        if "batch_size" in performance_config:
            batch_size = performance_config["batch_size"]
            if not isinstance(batch_size, int) or batch_size <= 0:
                raise ValidationError("Batch size must be a positive integer")
        
        if "max_connections" in performance_config:
            max_connections = performance_config["max_connections"]
            if not isinstance(max_connections, int) or max_connections <= 0:
                raise ValidationError("Max connections must be a positive integer")
    
    def _parse_connection_config(self) -> QdrantConnectionConfig:
        """Parse connection configuration."""
        connection_config = self.config.get("connection", {})
        
        return QdrantConnectionConfig(
            host=connection_config.get("host", "192.168.10.30"),
            port=connection_config.get("port", 6333),
            grpc_port=connection_config.get("grpc_port", 6334),
            timeout=connection_config.get("timeout", 30.0),
            api_key=connection_config.get("api_key"),
            https=connection_config.get("https", False),
            prefix=connection_config.get("prefix")
        )
    
    def _parse_retry_config(self) -> QdrantRetryConfig:
        """Parse retry configuration."""
        retry_config = self.config.get("retry", {})
        
        return QdrantRetryConfig(
            max_attempts=retry_config.get("max_attempts", 3),
            base_delay=retry_config.get("base_delay", 1.0),
            max_delay=retry_config.get("max_delay", 60.0),
            exponential_base=retry_config.get("exponential_base", 2.0),
            jitter=retry_config.get("jitter", True)
        )
    
    def _parse_performance_config(self) -> QdrantPerformanceConfig:
        """Parse performance configuration."""
        performance_config = self.config.get("performance", {})
        
        return QdrantPerformanceConfig(
            batch_size=performance_config.get("batch_size", 1000),
            max_connections=performance_config.get("max_connections", 100),
            connection_timeout=performance_config.get("connection_timeout", 10.0),
            read_timeout=performance_config.get("read_timeout", 60.0),
            write_timeout=performance_config.get("write_timeout", 60.0),
            pool_size=performance_config.get("pool_size", 10),
            max_retries_per_request=performance_config.get("max_retries_per_request", 3)
        )
    
    def _parse_collection_defaults(self) -> QdrantCollectionDefaults:
        """Parse collection default configuration."""
        collection_config = self.config.get("collection_defaults", {})
        
        hnsw_config = collection_config.get("hnsw_config", {})
        default_hnsw = {
            "m": hnsw_config.get("m", 16),
            "ef_construct": hnsw_config.get("ef_construct", 100),
            "full_scan_threshold": hnsw_config.get("full_scan_threshold", 10000)
        }
        
        return QdrantCollectionDefaults(
            vector_size=collection_config.get("vector_size", 384),
            distance=collection_config.get("distance", "cosine"),
            shard_number=collection_config.get("shard_number", 1),
            replication_factor=collection_config.get("replication_factor", 1),
            write_consistency_factor=collection_config.get("write_consistency_factor", 1),
            on_disk_payload=collection_config.get("on_disk_payload", True),
            hnsw_config=default_hnsw
        )
    
    def get_connection_url(self, use_grpc: bool = False) -> str:
        """
        Get connection URL.
        
        Args:
            use_grpc: Whether to use gRPC connection
            
        Returns:
            Connection URL
        """
        protocol = "https" if self.connection.https else "http"
        port = self.connection.grpc_port if use_grpc else self.connection.port
        
        url = f"{protocol}://{self.connection.host}:{port}"
        
        if self.connection.prefix:
            url += f"/{self.connection.prefix.strip('/')}"
        
        return url
    
    def get_client_config(self) -> Dict[str, Any]:
        """
        Get client configuration dictionary.
        
        Returns:
            Client configuration
        """
        return {
            "url": self.get_connection_url(),
            "grpc_url": self.get_connection_url(use_grpc=True),
            "timeout": self.connection.timeout,
            "api_key": self.connection.api_key,
            "https": self.connection.https,
            "prefix": self.connection.prefix
        }
    
    def get_retry_config_dict(self) -> Dict[str, Any]:
        """
        Get retry configuration dictionary.
        
        Returns:
            Retry configuration
        """
        return {
            "max_attempts": self.retry.max_attempts,
            "base_delay": self.retry.base_delay,
            "max_delay": self.retry.max_delay,
            "exponential_base": self.retry.exponential_base,
            "jitter": self.retry.jitter
        }
    
    def get_performance_config_dict(self) -> Dict[str, Any]:
        """
        Get performance configuration dictionary.
        
        Returns:
            Performance configuration
        """
        return {
            "batch_size": self.performance.batch_size,
            "max_connections": self.performance.max_connections,
            "connection_timeout": self.performance.connection_timeout,
            "read_timeout": self.performance.read_timeout,
            "write_timeout": self.performance.write_timeout,
            "pool_size": self.performance.pool_size,
            "max_retries_per_request": self.performance.max_retries_per_request
        }
    
    def get_collection_defaults_dict(self) -> Dict[str, Any]:
        """
        Get collection defaults dictionary.
        
        Returns:
            Collection defaults
        """
        return {
            "vector_size": self.collection_defaults.vector_size,
            "distance": self.collection_defaults.distance,
            "shard_number": self.collection_defaults.shard_number,
            "replication_factor": self.collection_defaults.replication_factor,
            "write_consistency_factor": self.collection_defaults.write_consistency_factor,
            "on_disk_payload": self.collection_defaults.on_disk_payload,
            "hnsw_config": self.collection_defaults.hnsw_config
        }
    
    def update_connection_config(self, **kwargs):
        """
        Update connection configuration.
        
        Args:
            **kwargs: Connection parameters to update
        """
        for key, value in kwargs.items():
            if hasattr(self.connection, key):
                setattr(self.connection, key, value)
    
    def update_retry_config(self, **kwargs):
        """
        Update retry configuration.
        
        Args:
            **kwargs: Retry parameters to update
        """
        for key, value in kwargs.items():
            if hasattr(self.retry, key):
                setattr(self.retry, key, value)
    
    def update_performance_config(self, **kwargs):
        """
        Update performance configuration.
        
        Args:
            **kwargs: Performance parameters to update
        """
        for key, value in kwargs.items():
            if hasattr(self.performance, key):
                setattr(self.performance, key, value)
    
    def update_collection_defaults(self, **kwargs):
        """
        Update collection defaults.
        
        Args:
            **kwargs: Collection default parameters to update
        """
        for key, value in kwargs.items():
            if hasattr(self.collection_defaults, key):
                setattr(self.collection_defaults, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Configuration dictionary
        """
        return {
            "connection": {
                "host": self.connection.host,
                "port": self.connection.port,
                "grpc_port": self.connection.grpc_port,
                "timeout": self.connection.timeout,
                "api_key": self.connection.api_key,
                "https": self.connection.https,
                "prefix": self.connection.prefix
            },
            "retry": {
                "max_attempts": self.retry.max_attempts,
                "base_delay": self.retry.base_delay,
                "max_delay": self.retry.max_delay,
                "exponential_base": self.retry.exponential_base,
                "jitter": self.retry.jitter
            },
            "performance": {
                "batch_size": self.performance.batch_size,
                "max_connections": self.performance.max_connections,
                "connection_timeout": self.performance.connection_timeout,
                "read_timeout": self.performance.read_timeout,
                "write_timeout": self.performance.write_timeout,
                "pool_size": self.performance.pool_size,
                "max_retries_per_request": self.performance.max_retries_per_request
            },
            "collection_defaults": {
                "vector_size": self.collection_defaults.vector_size,
                "distance": self.collection_defaults.distance,
                "shard_number": self.collection_defaults.shard_number,
                "replication_factor": self.collection_defaults.replication_factor,
                "write_consistency_factor": self.collection_defaults.write_consistency_factor,
                "on_disk_payload": self.collection_defaults.on_disk_payload,
                "hnsw_config": self.collection_defaults.hnsw_config
            }
        }
    
    def validate_collection_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and merge collection configuration with defaults.
        
        Args:
            config: Collection configuration
            
        Returns:
            Validated configuration
        """
        # Start with defaults
        validated = self.get_collection_defaults_dict()
        
        # Override with provided config
        if "vector_size" in config:
            vector_size = config["vector_size"]
            if not isinstance(vector_size, int) or vector_size <= 0:
                raise ValidationError("Vector size must be a positive integer")
            validated["vector_size"] = vector_size
        
        if "distance" in config:
            distance = config["distance"]
            valid_distances = ["cosine", "euclidean", "dot", "manhattan"]
            if distance not in valid_distances:
                raise ValidationError(f"Distance must be one of: {valid_distances}")
            validated["distance"] = distance
        
        if "shard_number" in config:
            shard_number = config["shard_number"]
            if not isinstance(shard_number, int) or shard_number <= 0:
                raise ValidationError("Shard number must be a positive integer")
            validated["shard_number"] = shard_number
        
        if "replication_factor" in config:
            replication_factor = config["replication_factor"]
            if not isinstance(replication_factor, int) or replication_factor <= 0:
                raise ValidationError("Replication factor must be a positive integer")
            validated["replication_factor"] = replication_factor
        
        if "hnsw_config" in config:
            hnsw_config = config["hnsw_config"]
            if isinstance(hnsw_config, dict):
                validated["hnsw_config"].update(hnsw_config)
        
        return validated
    
    def get_optimal_batch_size(self, vector_size: int, operation: str = "insert") -> int:
        """
        Get optimal batch size based on vector size and operation.
        
        Args:
            vector_size: Vector dimension
            operation: Operation type
            
        Returns:
            Optimal batch size
        """
        base_batch_size = self.performance.batch_size
        
        # Adjust based on vector size
        if vector_size > 1000:
            base_batch_size = max(100, base_batch_size // 2)
        elif vector_size > 2000:
            base_batch_size = max(50, base_batch_size // 4)
        
        # Adjust based on operation
        if operation == "search":
            base_batch_size = min(base_batch_size, 100)
        elif operation == "update":
            base_batch_size = min(base_batch_size, 500)
        
        return base_batch_size
    
    def get_connection_health_check_config(self) -> Dict[str, Any]:
        """
        Get configuration for connection health checks.
        
        Returns:
            Health check configuration
        """
        return {
            "url": self.get_connection_url(),
            "timeout": min(self.connection.timeout, 10.0),
            "retry_attempts": 2,
            "retry_delay": 1.0
        }
