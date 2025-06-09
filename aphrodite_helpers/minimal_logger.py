"""
Minimal logging configuration for Aphrodite
Focus on essential information only - errors, warnings, and key events
"""

import logging
import logging.handlers
import os
from typing import Optional

class MinimalLogger:
    def __init__(self, name: str = "aphrodite"):
        self.logger = logging.getLogger(name)
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup file handler only for essential logging"""
        # Create logs directory
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        self.logger.setLevel(logging.WARNING)  # Only WARNING and ERROR by default
        
        # File handler with rotation (5MB, keep 3 files)
        file_handler = logging.handlers.RotatingFileHandler(
            os.path.join(log_dir, "aphrodite.log"),
            maxBytes=5*1024*1024,
            backupCount=3,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.WARNING)
        
        # Minimal format - just timestamp, level, and message
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def get_logger(self, module_name: str):
        """Get a logger for a specific module"""
        return self.logger.getChild(module_name)

# Global logger instance
_minimal_logger = MinimalLogger()

def get_logger(module_name: str) -> logging.Logger:
    """Get a logger for the specified module"""
    return _minimal_logger.get_logger(module_name)

# Essential logging functions only
def log_error(message: str, module: str = "main"):
    """Log error - always logged and shown"""
    logger = get_logger(module)
    logger.error(message)
    print(f"❌ {message}")  # Still show errors on console

def log_warning(message: str, module: str = "main"):
    """Log warning - logged to file, optionally shown"""
    logger = get_logger(module)
    logger.warning(message)
    # Warnings shown only for important cases
    
def log_critical(message: str, module: str = "main"):
    """Log critical event - always logged and shown"""
    logger = get_logger(module)
    logger.critical(message)
    print(f"🚨 {message}")

def log_milestone(message: str, module: str = "main"):
    """Log important milestone - file only"""
    logger = get_logger(module)
    logger.warning(f"MILESTONE: {message}")  # Use WARNING level for milestones

# Context manager for operation tracking
class LoggedOperation:
    def __init__(self, operation_name: str, module: str = "main"):
        self.operation_name = operation_name
        self.module = module
        self.logger = get_logger(module)
    
    def __enter__(self):
        self.logger.warning(f"STARTED: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.logger.error(f"FAILED: {self.operation_name} - {exc_val}")
        else:
            self.logger.warning(f"COMPLETED: {self.operation_name}")
