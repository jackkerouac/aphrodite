"""
Logging System Initialization

Central logging setup for Aphrodite v2 that provides structured logging
with correlation IDs and consistent formatting across all services.
"""

import os
import yaml
import logging
import logging.config
from pathlib import Path
from typing import Optional, Dict, Any

# Import custom formatters
from .formatters.json_formatter import JSONFormatter, CorrelationJSONFormatter

class LoggingManager:
    """
    Centralized logging manager for Aphrodite v2
    """
    
    def __init__(self):
        self.config_dir = Path(__file__).parent / "config"
        self.log_dir = Path(__file__).parent.parent / "logs"
        self.current_config: Optional[Dict[str, Any]] = None
        
        # Ensure log directory exists
        self.log_dir.mkdir(exist_ok=True)
    
    def setup_logging(self, environment: str = "development", config_override: Optional[Dict[str, Any]] = None):
        """
        Setup logging configuration for the specified environment
        
        Args:
            environment: The environment name (development, production, etc.)
            config_override: Optional dictionary to override config values
        """
        
        # Load base config
        base_config_path = self.config_dir / "base.yaml"
        config = self._load_config(base_config_path)
        
        # Load environment-specific config
        env_config_path = self.config_dir / f"{environment}.yaml"
        if env_config_path.exists():
            env_config = self._load_config(env_config_path)
            config = self._merge_configs(config, env_config)
        
        # Apply overrides
        if config_override:
            config = self._merge_configs(config, config_override)
        
        # Ensure log directory exists in config paths and handle permission issues
        self._ensure_log_directories(config)
        
        # Check if we still have any handlers left
        if not config.get("handlers"):
            print("Warning: No handlers available, using console-only fallback")
            config = self._get_fallback_config()
        
        try:
            # Apply configuration
            logging.config.dictConfig(config)
            
            # Store current config
            self.current_config = config
            
            # Log the initialization
            logger = logging.getLogger("aphrodite.logging")
            logger.info(f"Logging initialized for environment: {environment}")
        except Exception as e:
            print(f"Warning: Failed to apply logging config: {e}")
            print("Using basic console logging fallback")
            self._setup_fallback_logging()
            self.current_config = {}
    
    def _load_config(self, config_path: Path) -> Dict[str, Any]:
        """Load YAML configuration file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            return {}
        except yaml.YAMLError as e:
            print(f"Error loading logging config {config_path}: {e}")
            return {}
    
    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge configuration dictionaries"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _ensure_log_directories(self, config: Dict[str, Any]):
        """Ensure all log file directories exist and are writable"""
        handlers = config.get("handlers", {})
        
        for handler_name, handler_config in handlers.items():
            if "filename" in handler_config:
                log_file = Path(handler_config["filename"])
                try:
                    log_file.parent.mkdir(parents=True, exist_ok=True)
                    # Test write permissions by creating/touching the file
                    log_file.touch(exist_ok=True)
                except (PermissionError, OSError) as e:
                    print(f"Warning: Cannot write to log file {log_file}: {e}")
                    print(f"Disabling file handler '{handler_name}' due to permission issues")
                    # Remove the problematic file handler from config
                    if handler_name in config.get("handlers", {}):
                        del config["handlers"][handler_name]
                    
                    # Remove handler from all loggers
                    for logger_config in config.get("loggers", {}).values():
                        if "handlers" in logger_config and handler_name in logger_config["handlers"]:
                            logger_config["handlers"].remove(handler_name)
                    
                    # Remove from root logger
                    if "handlers" in config.get("root", {}) and handler_name in config["root"]["handlers"]:
                        config["root"]["handlers"].remove(handler_name)
    
    def _get_fallback_config(self) -> Dict[str, Any]:
        """Get a basic console-only logging configuration"""
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "simple": {
                    "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S"
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": "INFO",
                    "formatter": "simple",
                    "stream": "ext://sys.stdout"
                }
            },
            "root": {
                "level": "INFO",
                "handlers": ["console"]
            }
        }
    
    def _setup_fallback_logging(self):
        """Setup basic console logging as fallback"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            force=True
        )
    
    def get_logger(self, name: str, **extra_fields) -> logging.Logger:
        """
        Get a logger with optional extra fields for structured logging
        
        Args:
            name: Logger name
            **extra_fields: Additional fields to include in all log messages
        
        Returns:
            Configured logger instance
        """
        logger = logging.getLogger(name)
        
        # Add extra fields as a custom attribute
        if extra_fields:
            # Create a custom adapter that adds extra fields
            return LoggerAdapter(logger, extra_fields)
        
        return logger

class LoggerAdapter(logging.LoggerAdapter):
    """
    Logger adapter that adds extra fields to log records
    """
    
    def process(self, msg, kwargs):
        # Add extra fields to the log record
        extra = kwargs.get('extra', {})
        extra.update(self.extra)
        kwargs['extra'] = extra
        
        return msg, kwargs

# Global logging manager instance
_logging_manager = LoggingManager()

def setup_logging(environment: str = None, config_override: Optional[Dict[str, Any]] = None):
    """
    Convenience function to setup logging
    
    Args:
        environment: Environment name (defaults to ENVIRONMENT env var or auto-detected)
        config_override: Optional configuration overrides
    """
    if environment is None:
        # Auto-detect environment
        environment = os.getenv("ENVIRONMENT")
        if environment is None:
            # Check if we're running in Docker
            if os.path.exists("/.dockerenv") or os.getenv("DOCKER_CONTAINER") == "true":
                environment = "production"
            else:
                environment = "development"
    
    _logging_manager.setup_logging(environment, config_override)

def get_logger(name: str, **extra_fields) -> logging.Logger:
    """
    Convenience function to get a logger
    
    Args:
        name: Logger name
        **extra_fields: Additional fields for structured logging
    
    Returns:
        Configured logger instance
    """
    return _logging_manager.get_logger(name, **extra_fields)

# Auto-initialize logging when module is imported
# Wrap in try-catch to handle permission issues gracefully
try:
    if not _logging_manager.current_config:
        setup_logging()
except Exception as e:
    print(f"Warning: Failed to initialize logging: {e}")
    print("Falling back to basic console logging")
    # Set up minimal console-only logging as fallback
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
