"""
Structured Logger
================

Operational logging with structured output for vector database operations.
Provides comprehensive logging with context and performance tracking.
"""

import logging
import json
import time
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from contextlib import contextmanager
from enum import Enum


class LogLevel(Enum):
    """Log level enumeration."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class StructuredLogger:
    """
    Structured logger for vector database operations.
    Provides comprehensive logging with context and performance tracking.
    """
    
    def __init__(self, name: str = "hana_x_vector", config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
        
        # Logger configuration
        log_config = self.config.get("logging", {})
        self.log_level = log_config.get("level", "INFO")
        self.log_format = log_config.get("format", "json")
        self.log_file = log_config.get("file")
        self.max_file_size = log_config.get("max_file_size", 100 * 1024 * 1024)  # 100MB
        self.backup_count = log_config.get("backup_count", 5)
        
        # Context tracking
        self.context = {}
        self.request_id = None
        
        # Performance tracking
        self.operation_timers = {}
        
        # Initialize logger
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup the underlying logger."""
        logger = logging.getLogger(self.name)
        logger.setLevel(getattr(logging, self.log_level.upper()))
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Create formatter
        if self.log_format == "json":
            formatter = self._create_json_formatter()
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler (if configured)
        if self.log_file:
            from logging.handlers import RotatingFileHandler
            file_handler = RotatingFileHandler(
                self.log_file,
                maxBytes=self.max_file_size,
                backupCount=self.backup_count
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    def _create_json_formatter(self):
        """Create JSON formatter."""
        class JSONFormatter(logging.Formatter):
            def format(self, record):
                log_entry = {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                    "module": record.module,
                    "function": record.funcName,
                    "line": record.lineno
                }
                
                # Add context if available
                if hasattr(record, 'context'):
                    log_entry["context"] = record.context
                
                # Add request ID if available
                if hasattr(record, 'request_id'):
                    log_entry["request_id"] = record.request_id
                
                # Add extra fields
                for key, value in record.__dict__.items():
                    if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 
                                  'pathname', 'filename', 'module', 'lineno', 
                                  'funcName', 'created', 'msecs', 'relativeCreated',
                                  'thread', 'threadName', 'processName', 'process',
                                  'message', 'exc_info', 'exc_text', 'stack_info',
                                  'context', 'request_id']:
                        log_entry[key] = value
                
                return json.dumps(log_entry)
        
        return JSONFormatter()
    
    def set_context(self, **kwargs):
        """
        Set logging context.
        
        Args:
            **kwargs: Context key-value pairs
        """
        self.context.update(kwargs)
    
    def clear_context(self):
        """Clear logging context."""
        self.context.clear()
    
    def set_request_id(self, request_id: str):
        """
        Set request ID for correlation.
        
        Args:
            request_id: Request identifier
        """
        self.request_id = request_id
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self._log(LogLevel.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self._log(LogLevel.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self._log(LogLevel.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self._log(LogLevel.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self._log(LogLevel.CRITICAL, message, **kwargs)
    
    def _log(self, level: LogLevel, message: str, **kwargs):
        """Internal logging method."""
        # Create log record
        extra = {
            'context': self.context.copy(),
            'request_id': self.request_id,
            **kwargs
        }
        
        # Log with appropriate level
        log_method = getattr(self.logger, level.value.lower())
        log_method(message, extra=extra)
    
    @contextmanager
    def operation_timer(self, operation_name: str, **context):
        """
        Context manager for timing operations.
        
        Args:
            operation_name: Name of the operation
            **context: Additional context
        """
        start_time = time.time()
        operation_id = f"{operation_name}_{int(start_time * 1000)}"
        
        # Log operation start
        self.info(f"Starting operation: {operation_name}", 
                 operation_id=operation_id, 
                 operation_name=operation_name,
                 **context)
        
        try:
            yield operation_id
        except Exception as e:
            # Log operation failure
            duration = time.time() - start_time
            self.error(f"Operation failed: {operation_name}",
                      operation_id=operation_id,
                      operation_name=operation_name,
                      duration=duration,
                      error=str(e),
                      **context)
            raise
        else:
            # Log operation success
            duration = time.time() - start_time
            self.info(f"Operation completed: {operation_name}",
                     operation_id=operation_id,
                     operation_name=operation_name,
                     duration=duration,
                     **context)
    
    def log_vector_operation(
        self,
        operation: str,
        collection: str,
        vector_count: int,
        duration: float,
        success: bool = True,
        error: Optional[str] = None,
        **kwargs
    ):
        """
        Log vector database operation.
        
        Args:
            operation: Operation type
            collection: Collection name
            vector_count: Number of vectors processed
            duration: Operation duration
            success: Whether operation succeeded
            error: Error message if failed
            **kwargs: Additional context
        """
        log_data = {
            "operation_type": "vector_operation",
            "operation": operation,
            "collection": collection,
            "vector_count": vector_count,
            "duration": duration,
            "success": success,
            "throughput": vector_count / duration if duration > 0 else 0,
            **kwargs
        }
        
        if error:
            log_data["error"] = error
        
        if success:
            self.info(f"Vector operation completed: {operation}", **log_data)
        else:
            self.error(f"Vector operation failed: {operation}", **log_data)
    
    def log_api_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        duration: float,
        request_size: Optional[int] = None,
        response_size: Optional[int] = None,
        user_agent: Optional[str] = None,
        **kwargs
    ):
        """
        Log API request.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            status_code: HTTP status code
            duration: Request duration
            request_size: Request size in bytes
            response_size: Response size in bytes
            user_agent: User agent string
            **kwargs: Additional context
        """
        log_data = {
            "operation_type": "api_request",
            "method": method,
            "endpoint": endpoint,
            "status_code": status_code,
            "duration": duration,
            **kwargs
        }
        
        if request_size is not None:
            log_data["request_size"] = request_size
        
        if response_size is not None:
            log_data["response_size"] = response_size
        
        if user_agent:
            log_data["user_agent"] = user_agent
        
        if status_code >= 400:
            self.warning(f"API request failed: {method} {endpoint}", **log_data)
        else:
            self.info(f"API request: {method} {endpoint}", **log_data)
    
    def log_external_model_request(
        self,
        model_name: str,
        text_count: int,
        duration: float,
        success: bool = True,
        error: Optional[str] = None,
        token_count: Optional[int] = None,
        **kwargs
    ):
        """
        Log external model request.
        
        Args:
            model_name: Name of the model
            text_count: Number of texts processed
            duration: Request duration
            success: Whether request succeeded
            error: Error message if failed
            token_count: Number of tokens processed
            **kwargs: Additional context
        """
        log_data = {
            "operation_type": "external_model_request",
            "model_name": model_name,
            "text_count": text_count,
            "duration": duration,
            "success": success,
            **kwargs
        }
        
        if token_count is not None:
            log_data["token_count"] = token_count
            log_data["tokens_per_second"] = token_count / duration if duration > 0 else 0
        
        if error:
            log_data["error"] = error
        
        if success:
            self.info(f"External model request completed: {model_name}", **log_data)
        else:
            self.error(f"External model request failed: {model_name}", **log_data)
    
    def log_cache_operation(
        self,
        operation: str,
        cache_type: str,
        key: str,
        hit: Optional[bool] = None,
        duration: Optional[float] = None,
        **kwargs
    ):
        """
        Log cache operation.
        
        Args:
            operation: Cache operation type
            cache_type: Type of cache
            key: Cache key
            hit: Whether cache hit occurred
            duration: Operation duration
            **kwargs: Additional context
        """
        log_data = {
            "operation_type": "cache_operation",
            "operation": operation,
            "cache_type": cache_type,
            "key": key,
            **kwargs
        }
        
        if hit is not None:
            log_data["hit"] = hit
        
        if duration is not None:
            log_data["duration"] = duration
        
        self.debug(f"Cache operation: {operation}", **log_data)
    
    def log_health_check(
        self,
        check_name: str,
        status: str,
        duration: float,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        Log health check result.
        
        Args:
            check_name: Name of the health check
            status: Health check status
            duration: Check duration
            message: Status message
            details: Additional details
            **kwargs: Additional context
        """
        log_data = {
            "operation_type": "health_check",
            "check_name": check_name,
            "status": status,
            "duration": duration,
            "message": message,
            **kwargs
        }
        
        if details:
            log_data["details"] = details
        
        if status == "healthy":
            self.debug(f"Health check passed: {check_name}", **log_data)
        else:
            self.warning(f"Health check failed: {check_name}", **log_data)
    
    def log_performance_metrics(
        self,
        metrics: Dict[str, Any],
        **kwargs
    ):
        """
        Log performance metrics.
        
        Args:
            metrics: Performance metrics
            **kwargs: Additional context
        """
        log_data = {
            "operation_type": "performance_metrics",
            "metrics": metrics,
            **kwargs
        }
        
        self.info("Performance metrics", **log_data)
    
    def log_error_with_traceback(
        self,
        message: str,
        exception: Exception,
        **kwargs
    ):
        """
        Log error with full traceback.
        
        Args:
            message: Error message
            exception: Exception object
            **kwargs: Additional context
        """
        import traceback
        
        log_data = {
            "operation_type": "error",
            "exception_type": type(exception).__name__,
            "exception_message": str(exception),
            "traceback": traceback.format_exc(),
            **kwargs
        }
        
        self.error(message, **log_data)
    
    def get_log_stats(self) -> Dict[str, Any]:
        """
        Get logging statistics.
        
        Returns:
            Logging statistics
        """
        # This would be implemented with actual log analysis
        # For now, return basic info
        return {
            "logger_name": self.name,
            "log_level": self.log_level,
            "log_format": self.log_format,
            "handlers": len(self.logger.handlers),
            "context_keys": list(self.context.keys()),
            "request_id": self.request_id
        }
    
    async def flush_logs(self):
        """Flush all log handlers."""
        for handler in self.logger.handlers:
            handler.flush()
    
    def create_child_logger(self, name: str) -> 'StructuredLogger':
        """
        Create child logger with inherited context.
        
        Args:
            name: Child logger name
            
        Returns:
            Child logger instance
        """
        child_name = f"{self.name}.{name}"
        child_logger = StructuredLogger(child_name, self.config)
        child_logger.context = self.context.copy()
        child_logger.request_id = self.request_id
        
        return child_logger
    
    @contextmanager
    def request_context(self, request_id: str, **context):
        """
        Context manager for request-scoped logging.
        
        Args:
            request_id: Request identifier
            **context: Request context
        """
        # Save current state
        old_request_id = self.request_id
        old_context = self.context.copy()
        
        try:
            # Set request context
            self.set_request_id(request_id)
            self.set_context(**context)
            
            yield
            
        finally:
            # Restore previous state
            self.request_id = old_request_id
            self.context = old_context
    
    def configure_sampling(self, sample_rate: float = 1.0):
        """
        Configure log sampling.
        
        Args:
            sample_rate: Sampling rate (0.0 to 1.0)
        """
        # This would implement log sampling for high-volume scenarios
        # For now, just store the configuration
        self.sample_rate = sample_rate
    
    def set_log_level(self, level: str):
        """
        Set log level dynamically.
        
        Args:
            level: Log level string
        """
        self.log_level = level.upper()
        self.logger.setLevel(getattr(logging, self.log_level))
    
    def add_log_filter(self, filter_func: callable):
        """
        Add custom log filter.
        
        Args:
            filter_func: Filter function
        """
        for handler in self.logger.handlers:
            handler.addFilter(filter_func)
