"""
Logging Configuration Module

Centralized logging setup following HXP Governance Coding Standards.
Implements Single Responsibility Principle for logging configuration.

Author: Citadel AI Team
License: MIT
"""

import logging
import logging.handlers
import sys
from typing import Optional, Dict, Any
from pathlib import Path
import structlog
from datetime import datetime


def setup_logging(config: Optional[Dict[str, Any]] = None) -> None:
    """
    Setup centralized logging configuration.
    
    Args:
        config: Optional logging configuration dictionary
    """
    # Default configuration
    default_config = {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file_path": None,
        "max_bytes": 10485760,  # 10MB
        "backup_count": 5,
        "structured": True
    }
    
    if config:
        logging_config = config.get("logging", {})
        default_config.update(logging_config)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, default_config["level"].upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(default_config["format"])
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if specified)
    if default_config["file_path"]:
        file_path = Path(default_config["file_path"])
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            file_path,
            maxBytes=default_config["max_bytes"],
            backupCount=default_config["backup_count"]
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Setup structured logging if enabled
    if default_config.get("structured", False):
        setup_structured_logging()
    
    # Log initialization
    logger = logging.getLogger(__name__)
    logger.info("Logging configuration initialized")


def setup_structured_logging() -> None:
    """Setup structured logging with structlog."""
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get logger instance with proper configuration.
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


class PerformanceLogger:
    """Performance logging utility (Single Responsibility Principle)."""
    
    def __init__(self, logger_name: str = "performance"):
        """Initialize performance logger."""
        self.logger = logging.getLogger(logger_name)
    
    def log_operation(self, operation: str, duration_ms: float, **kwargs) -> None:
        """Log operation performance."""
        self.logger.info(
            f"Operation: {operation}, Duration: {duration_ms:.2f}ms",
            extra={
                "operation": operation,
                "duration_ms": duration_ms,
                **kwargs
            }
        )
    
    def log_query(self, query_type: str, collection: str, duration_ms: float, 
                  result_count: int = 0) -> None:
        """Log query performance."""
        self.log_operation(
            f"{query_type}_query",
            duration_ms,
            collection=collection,
            result_count=result_count
        )
    
    def log_embedding(self, model: str, text_count: int, duration_ms: float) -> None:
        """Log embedding generation performance."""
        self.log_operation(
            "embedding_generation",
            duration_ms,
            model=model,
            text_count=text_count,
            avg_duration_per_text=duration_ms / text_count if text_count > 0 else 0
        )


class AuditLogger:
    """Audit logging utility (Single Responsibility Principle)."""
    
    def __init__(self, logger_name: str = "audit"):
        """Initialize audit logger."""
        self.logger = logging.getLogger(logger_name)
    
    def log_api_request(self, method: str, endpoint: str, user_id: Optional[str] = None,
                       status_code: int = 200, duration_ms: float = 0.0) -> None:
        """Log API request."""
        self.logger.info(
            f"API Request: {method} {endpoint}",
            extra={
                "event_type": "api_request",
                "method": method,
                "endpoint": endpoint,
                "user_id": user_id,
                "status_code": status_code,
                "duration_ms": duration_ms,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    def log_vector_operation(self, operation: str, collection: str, 
                           vector_count: int = 1, user_id: Optional[str] = None) -> None:
        """Log vector database operation."""
        self.logger.info(
            f"Vector Operation: {operation}",
            extra={
                "event_type": "vector_operation",
                "operation": operation,
                "collection": collection,
                "vector_count": vector_count,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    def log_external_model_call(self, model_id: str, operation: str,
                              success: bool, duration_ms: float = 0.0,
                              tokens_used: int = 0) -> None:
        """Log external model API call."""
        self.logger.info(
            f"External Model Call: {model_id} - {operation}",
            extra={
                "event_type": "external_model_call",
                "model_id": model_id,
                "operation": operation,
                "success": success,
                "duration_ms": duration_ms,
                "tokens_used": tokens_used,
                "timestamp": datetime.now().isoformat()
            }
        )


class SecurityLogger:
    """Security logging utility (Single Responsibility Principle)."""
    
    def __init__(self, logger_name: str = "security"):
        """Initialize security logger."""
        self.logger = logging.getLogger(logger_name)
    
    def log_authentication_attempt(self, user_id: str, success: bool,
                                 ip_address: Optional[str] = None) -> None:
        """Log authentication attempt."""
        self.logger.warning(
            f"Authentication {'successful' if success else 'failed'} for user: {user_id}",
            extra={
                "event_type": "authentication",
                "user_id": user_id,
                "success": success,
                "ip_address": ip_address,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    def log_rate_limit_exceeded(self, endpoint: str, ip_address: Optional[str] = None,
                              user_id: Optional[str] = None) -> None:
        """Log rate limit exceeded."""
        self.logger.warning(
            f"Rate limit exceeded for endpoint: {endpoint}",
            extra={
                "event_type": "rate_limit_exceeded",
                "endpoint": endpoint,
                "ip_address": ip_address,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    def log_suspicious_activity(self, activity_type: str, details: Dict[str, Any],
                              ip_address: Optional[str] = None) -> None:
        """Log suspicious activity."""
        self.logger.error(
            f"Suspicious activity detected: {activity_type}",
            extra={
                "event_type": "suspicious_activity",
                "activity_type": activity_type,
                "details": details,
                "ip_address": ip_address,
                "timestamp": datetime.now().isoformat()
            }
        )
