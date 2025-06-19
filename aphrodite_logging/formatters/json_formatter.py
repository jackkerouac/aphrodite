"""
JSON Formatter for Structured Logging

Provides consistent JSON formatting across all Aphrodite v2 services.
"""

import json
import logging
import traceback
from datetime import datetime
from typing import Dict, Any, Optional

class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter that creates structured log entries
    with consistent fields across all services.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hostname = self._get_hostname()
    
    def _get_hostname(self) -> str:
        """Get the hostname for log entries"""
        try:
            import socket
            return socket.gethostname()
        except Exception:
            return "unknown"
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        
        # Base log entry structure
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "hostname": self.hostname,
            "process_id": record.process,
            "thread_id": record.thread,
        }
        
        # Add correlation ID if present
        correlation_id = getattr(record, 'correlation_id', None)
        if correlation_id:
            log_entry["correlation_id"] = correlation_id
        
        # Add request ID if present
        request_id = getattr(record, 'request_id', None)
        if request_id:
            log_entry["request_id"] = request_id
        
        # Add user ID if present
        user_id = getattr(record, 'user_id', None)
        if user_id:
            log_entry["user_id"] = user_id
        
        # Add service name if present
        service = getattr(record, 'service', None)
        if service:
            log_entry["service"] = service
        
        # Add extra fields
        extra_fields = getattr(record, 'extra_fields', {})
        if extra_fields and isinstance(extra_fields, dict):
            log_entry.update(extra_fields)
        
        # Add exception information if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # Add stack trace if present
        if record.stack_info:
            log_entry["stack_trace"] = record.stack_info
        
        # Convert to JSON
        try:
            return json.dumps(log_entry, default=str, ensure_ascii=False)
        except (TypeError, ValueError) as e:
            # Fallback to basic logging if JSON serialization fails
            fallback_entry = {
                "timestamp": datetime.fromtimestamp(record.created).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": f"JSON serialization failed: {e}. Original message: {record.getMessage()}",
                "hostname": self.hostname
            }
            return json.dumps(fallback_entry, ensure_ascii=False)

class CorrelationJSONFormatter(JSONFormatter):
    """
    Enhanced JSON formatter that always includes correlation tracking
    """
    
    def format(self, record: logging.LogRecord) -> str:
        # Ensure correlation ID is present
        if not hasattr(record, 'correlation_id'):
            record.correlation_id = self._generate_correlation_id()
        
        return super().format(record)
    
    def _generate_correlation_id(self) -> str:
        """Generate a correlation ID if none exists"""
        import uuid
        return str(uuid.uuid4())[:8]
