"""
Logging utilities for HANA-X infrastructure.

This module provides common logging configuration and utilities that can be
reused across Enterprise and LoB server projects.
"""

import logging
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional, Union
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import threading
from contextlib import contextmanager


class HanaXFormatter(logging.Formatter):
    """
    Custom formatter for HANA-X infrastructure logging.
    
    Provides structured logging with server identification and context.
    """
    
    def __init__(self, 
                 server_id: str,
                 include_server_id: bool = True,
                 json_format: bool = False,
                 *args, **kwargs):
        """
        Initialize the formatter.
        
        Args:
            server_id: Server identifier to include in logs
            include_server_id: Whether to include server ID in logs
            json_format: Whether to use JSON format for structured logging
        """
        super().__init__(*args, **kwargs)
        self.server_id = server_id
        self.include_server_id = include_server_id
        self.json_format = json_format
        
        if not json_format:
            # Standard format with server ID
            self._fmt = (
                '%(asctime)s - %(name)s - %(levelname)s - '
                f'[{server_id}] - %(message)s'
            )
        else:
            self._fmt = None
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record.
        
        Args:
            record: Log record to format
            
        Returns:
            Formatted log message
        """
        if self.json_format:
            return self._format_json(record)
        else:
            return self._format_standard(record)
    
    def _format_json(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        if self.include_server_id:
            log_entry['server_id'] = self.server_id
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry)
    
    def _format_standard(self, record: logging.LogRecord) -> str:
        """Format log record in standard format."""
        if self.include_server_id:
            # Add server ID context to the message
            original_msg = record.getMessage()
            record.msg = f"[{self.server_id}] {original_msg}"
            record.args = ()
        
        return super().format(record)


class HanaXLoggerAdapter(logging.LoggerAdapter):
    """
    Logger adapter that adds contextual information to log records.
    """
    
    def __init__(self, logger: logging.Logger, extra: Dict[str, Any]):
        """
        Initialize the adapter.
        
        Args:
            logger: Logger instance to adapt
            extra: Extra context to add to log records
        """
        super().__init__(logger, extra)
        self.context_stack = []
    
    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """
        Process log message and add context.
        
        Args:
            msg: Log message
            kwargs: Keyword arguments
            
        Returns:
            Processed message and kwargs
        """
        # Add extra context from the stack
        if self.context_stack:
            context = " | ".join(self.context_stack)
            msg = f"[{context}] {msg}"
        
        return super().process(msg, kwargs)
    
    @contextmanager
    def context(self, context_info: str):
        """
        Context manager for adding temporary context to logs.
        
        Args:
            context_info: Context information to add
        """
        self.context_stack.append(context_info)
        try:
            yield
        finally:
            self.context_stack.pop()


class HanaXLogger:
    """
    Main logger configuration and management class for HANA-X infrastructure.
    """
    
    def __init__(self, 
                 server_id: str,
                 log_dir: Union[str, Path] = "logs",
                 log_level: str = "INFO",
                 json_format: bool = False,
                 enable_console: bool = True,
                 enable_file: bool = True,
                 max_file_size: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 5):
        """
        Initialize the HANA-X logger.
        
        Args:
            server_id: Server identifier
            log_dir: Directory for log files
            log_level: Logging level
            json_format: Whether to use JSON format
            enable_console: Whether to enable console logging
            enable_file: Whether to enable file logging
            max_file_size: Maximum file size before rotation
            backup_count: Number of backup files to keep
        """
        self.server_id = server_id
        self.log_dir = Path(log_dir)
        self.log_level = getattr(logging, log_level.upper())
        self.json_format = json_format
        self.enable_console = enable_console
        self.enable_file = enable_file
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        
        # Create log directory
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Thread-local storage for context
        self.local = threading.local()
        
        # Configure logging
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Set up logging configuration."""
        # Create formatters
        self.formatter = HanaXFormatter(
            server_id=self.server_id,
            json_format=self.json_format
        )
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(self.log_level)
        
        # Remove existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Add console handler
        if self.enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.log_level)
            console_handler.setFormatter(self.formatter)
            root_logger.addHandler(console_handler)
        
        # Add file handlers
        if self.enable_file:
            self._setup_file_handlers(root_logger)
    
    def _setup_file_handlers(self, root_logger: logging.Logger) -> None:
        """Set up file handlers for different log levels."""
        # General log file
        general_handler = RotatingFileHandler(
            self.log_dir / f"{self.server_id}_general.log",
            maxBytes=self.max_file_size,
            backupCount=self.backup_count
        )
        general_handler.setLevel(self.log_level)
        general_handler.setFormatter(self.formatter)
        root_logger.addHandler(general_handler)
        
        # Error log file
        error_handler = RotatingFileHandler(
            self.log_dir / f"{self.server_id}_error.log",
            maxBytes=self.max_file_size,
            backupCount=self.backup_count
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(self.formatter)
        root_logger.addHandler(error_handler)
        
        # Access log file (for API requests)
        access_handler = RotatingFileHandler(
            self.log_dir / f"{self.server_id}_access.log",
            maxBytes=self.max_file_size,
            backupCount=self.backup_count
        )
        access_handler.setLevel(logging.INFO)
        access_handler.setFormatter(self.formatter)
        
        # Create access logger
        access_logger = logging.getLogger(f"{self.server_id}.access")
        access_logger.addHandler(access_handler)
        access_logger.setLevel(logging.INFO)
        access_logger.propagate = False
    
    def get_logger(self, name: str) -> HanaXLoggerAdapter:
        """
        Get a logger instance with context.
        
        Args:
            name: Logger name
            
        Returns:
            Logger adapter with context
        """
        logger = logging.getLogger(name)
        return HanaXLoggerAdapter(logger, {
            'server_id': self.server_id,
            'component': name
        })
    
    def log_api_request(self, 
                       method: str,
                       path: str,
                       status_code: int,
                       latency_ms: float,
                       user_id: Optional[str] = None,
                       additional_info: Optional[Dict[str, Any]] = None) -> None:
        """
        Log an API request.
        
        Args:
            method: HTTP method
            path: Request path
            status_code: HTTP status code
            latency_ms: Request latency in milliseconds
            user_id: Optional user identifier
            additional_info: Optional additional information
        """
        access_logger = logging.getLogger(f"{self.server_id}.access")
        
        log_data = {
            'method': method,
            'path': path,
            'status_code': status_code,
            'latency_ms': latency_ms,
            'timestamp': datetime.now().isoformat()
        }
        
        if user_id:
            log_data['user_id'] = user_id
        
        if additional_info:
            log_data.update(additional_info)
        
        if self.json_format:
            access_logger.info(json.dumps(log_data))
        else:
            access_logger.info(
                f"{method} {path} {status_code} {latency_ms:.2f}ms"
                f"{f' user:{user_id}' if user_id else ''}"
            )
    
    def log_performance_metric(self, 
                             metric_name: str,
                             value: float,
                             unit: str = "",
                             tags: Optional[Dict[str, str]] = None) -> None:
        """
        Log a performance metric.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            unit: Unit of measurement
            tags: Optional tags for the metric
        """
        metrics_logger = logging.getLogger(f"{self.server_id}.metrics")
        
        log_data = {
            'metric_name': metric_name,
            'value': value,
            'unit': unit,
            'timestamp': datetime.now().isoformat()
        }
        
        if tags:
            log_data['tags'] = tags
        
        if self.json_format:
            metrics_logger.info(json.dumps(log_data))
        else:
            tags_str = f" tags:{tags}" if tags else ""
            metrics_logger.info(f"METRIC {metric_name}={value}{unit}{tags_str}")
    
    def log_security_event(self, 
                          event_type: str,
                          severity: str,
                          message: str,
                          user_id: Optional[str] = None,
                          source_ip: Optional[str] = None,
                          additional_data: Optional[Dict[str, Any]] = None) -> None:
        """
        Log a security event.
        
        Args:
            event_type: Type of security event
            severity: Severity level
            message: Event message
            user_id: Optional user identifier
            source_ip: Optional source IP address
            additional_data: Optional additional data
        """
        security_logger = logging.getLogger(f"{self.server_id}.security")
        
        log_data = {
            'event_type': event_type,
            'severity': severity,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        
        if user_id:
            log_data['user_id'] = user_id
        if source_ip:
            log_data['source_ip'] = source_ip
        if additional_data:
            log_data.update(additional_data)
        
        # Log at appropriate level based on severity
        log_level = getattr(logging, severity.upper(), logging.INFO)
        
        if self.json_format:
            security_logger.log(log_level, json.dumps(log_data))
        else:
            security_logger.log(log_level, f"SECURITY {event_type}: {message}")
    
    def configure_specific_logger(self, 
                                 logger_name: str,
                                 log_file: Optional[str] = None,
                                 log_level: Optional[str] = None) -> logging.Logger:
        """
        Configure a specific logger with custom settings.
        
        Args:
            logger_name: Name of the logger
            log_file: Optional specific log file
            log_level: Optional specific log level
            
        Returns:
            Configured logger instance
        """
        logger = logging.getLogger(logger_name)
        
        if log_level:
            logger.setLevel(getattr(logging, log_level.upper()))
        
        if log_file:
            handler = RotatingFileHandler(
                self.log_dir / log_file,
                maxBytes=self.max_file_size,
                backupCount=self.backup_count
            )
            handler.setFormatter(self.formatter)
            logger.addHandler(handler)
            logger.propagate = False
        
        return logger
    
    def get_log_files(self) -> Dict[str, Path]:
        """
        Get paths to all log files.
        
        Returns:
            Dictionary mapping log types to file paths
        """
        return {
            'general': self.log_dir / f"{self.server_id}_general.log",
            'error': self.log_dir / f"{self.server_id}_error.log",
            'access': self.log_dir / f"{self.server_id}_access.log"
        }
    
    def cleanup_old_logs(self, days_to_keep: int = 30) -> None:
        """
        Clean up old log files.
        
        Args:
            days_to_keep: Number of days of logs to keep
        """
        import time
        
        cutoff_time = time.time() - (days_to_keep * 24 * 60 * 60)
        
        for log_file in self.log_dir.glob(f"{self.server_id}_*.log*"):
            if log_file.stat().st_mtime < cutoff_time:
                log_file.unlink()
                logging.info(f"Removed old log file: {log_file}")


def create_hana_logger(
    server_id: str,
    server_type: str = "generic",
    log_dir: Union[str, Path] = "logs",
    log_level: str = "INFO",
    json_format: bool = False,
    **kwargs
) -> HanaXLogger:
    """
    Create a HANA-X logger instance.
    
    Args:
        server_id: Server identifier
        server_type: Type of server (enterprise, lob, etc.)
        log_dir: Directory for log files
        log_level: Logging level
        json_format: Whether to use JSON format
        **kwargs: Additional arguments for HanaXLogger
        
    Returns:
        HanaXLogger instance
    """
    # Create server-specific log directory
    server_log_dir = Path(log_dir) / server_type
    
    return HanaXLogger(
        server_id=server_id,
        log_dir=server_log_dir,
        log_level=log_level,
        json_format=json_format,
        **kwargs
    )


def log_function_call(logger: logging.Logger):
    """
    Decorator to log function calls.
    
    Args:
        logger: Logger instance to use
        
    Returns:
        Decorator function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"Function {func.__name__} completed successfully")
                return result
            except Exception as e:
                logger.error(f"Function {func.__name__} failed with error: {e}")
                raise
        return wrapper
    return decorator
