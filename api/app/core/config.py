"""
Application Configuration Management

Centralized configuration using Pydantic Settings with environment variable support.
Enhanced with deployment-agnostic CORS handling.
"""

import os
import socket
from typing import List, Optional, Union, Any, Dict
from functools import lru_cache
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    debug: bool = Field(default=False, description="Debug mode")
    environment: str = Field(default="development", description="Environment name")
    
    # API Server
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    api_workers: int = Field(default=4, description="Number of API workers")
    api_reload: bool = Field(default=True, description="Enable auto-reload")
    
    # Container-friendly paths
    assets_dir: str = Field(default="/app/assets", description="Assets directory path")
    api_static_dir: str = Field(default="/app/api/static", description="API static files directory")
    aphrodite_root: str = Field(default="/app", description="Aphrodite project root directory")
    
    # Host validation - simple string field that we'll parse in the app
    allowed_hosts: str = Field(
        default="*",
        description="Allowed host headers (comma-separated or *)"
    )
    
    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://aphrodite:changeme@postgres:5432/aphrodite",
        description="Database connection URL"
    )
    database_pool_size: int = Field(default=20, description="Database connection pool size")
    database_max_overflow: int = Field(default=30, description="Database max overflow connections")
    
    def get_database_url(self) -> str:
        """Get database URL, building from individual env vars if available"""
        # Check if individual database environment variables are set
        db_host = os.environ.get('POSTGRES_HOST')
        db_port = os.environ.get('POSTGRES_PORT')
        db_name = os.environ.get('POSTGRES_DB')
        db_user = os.environ.get('POSTGRES_USER')
        db_password = os.environ.get('POSTGRES_PASSWORD')
        
        # Priority 1: If individual vars are set with explicit host, use them
        if all([db_host, db_port, db_name, db_user, db_password]):
            return f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        
        # Priority 2: If we have the individual vars but no host, assume local development
        if all([db_port, db_name, db_user, db_password]) and not db_host:
            # Use localhost with the external port for local development
            return f"postgresql+asyncpg://{db_user}:{db_password}@localhost:{db_port}/{db_name}"
        
        # Priority 3: Check if we're definitely in Docker
        is_docker = (
            os.path.exists('/.dockerenv') or  # Docker container indicator
            os.environ.get('DOCKER_ENV') == 'true'  # Explicit Docker flag
        )
        
        # Priority 4: If not in Docker and we have some individual DB settings, prefer localhost
        if not is_docker and db_port and db_user and db_password:
            db_name = db_name or 'aphrodite'
            return f"postgresql+asyncpg://{db_user}:{db_password}@localhost:{db_port}/{db_name}"
        
        # Priority 5: Default to the configured DATABASE_URL (for Docker or when no individual vars)
        return self.database_url
    
    # Redis
    redis_url: str = Field(
        default="redis://redis:6379/0",
        description="Redis connection URL"
    )
    redis_max_connections: int = Field(default=20, description="Redis max connections")
    
    # Celery
    celery_broker_url: str = Field(
        default="redis://redis:6379/0",
        description="Celery broker URL"
    )
    celery_result_backend: str = Field(
        default="redis://redis:6379/1",
        description="Celery result backend URL"
    )
    celery_max_retries: int = Field(default=3, description="Max Celery job retries")
    celery_retry_delay: int = Field(default=60, description="Celery retry delay in seconds")
    
    # Security
    secret_key: str = Field(
        default="development-secret-key-change-in-production",
        description="Secret key for JWT and encryption"
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_expire_minutes: int = Field(default=30, description="JWT expiration time in minutes")
    
    # CORS - Simple string field to avoid Pydantic issues
    cors_origins: str = Field(
        default="*",
        description="Allowed CORS origins (comma-separated or *)"
    )
    
    # Helper methods to parse string fields into lists
    def get_allowed_hosts_list(self) -> List[str]:
        """Get allowed hosts as a list"""
        if self.allowed_hosts == "*":
            return ["*"]
        return [host.strip() for host in self.allowed_hosts.split(',') if host.strip()]
    
    def get_cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list with deployment-agnostic defaults"""
        # If explicitly set to wildcard, allow everything
        if self.cors_origins == "*":
            return ["*"]
        
        # Parse explicit origins
        explicit_origins = [origin.strip() for origin in self.cors_origins.split(',') if origin.strip()]
        
        # If no explicit origins or in production, use smart defaults
        if not explicit_origins or self.environment.lower() == "production":
            return self._get_smart_cors_origins()
        
        return explicit_origins
    
    def _get_smart_cors_origins(self) -> List[str]:
        """Generate smart CORS origins based on deployment context"""
        origins = set()
        
        # Always allow common localhost variations for development/testing
        port = str(self.api_port)
        localhost_origins = [
            f"http://localhost:{port}",
            f"http://127.0.0.1:{port}",
            f"http://0.0.0.0:{port}"
        ]
        origins.update(localhost_origins)
        
        # Try to detect current machine's network interfaces
        try:
            # Get hostname
            hostname = socket.gethostname()
            if hostname and hostname != "localhost":
                origins.add(f"http://{hostname}:{port}")
            
            # Get local IP addresses
            for interface_info in socket.getaddrinfo(hostname, None):
                ip = interface_info[4][0]
                if ip and not ip.startswith("127.") and ":" not in ip:  # IPv4, not loopback
                    origins.add(f"http://{ip}:{port}")
        except Exception:
            # If network detection fails, don't crash
            pass
        
        # Check for Docker container networking
        try:
            # In Docker, try to get the host gateway IP
            with open('/proc/net/route', 'r') as f:
                for line in f:
                    fields = line.strip().split()
                    if fields[1] == "00000000":  # Default route
                        gateway_hex = fields[2]
                        gateway_ip = socket.inet_ntoa(bytes.fromhex(gateway_hex)[::-1])
                        if gateway_ip and gateway_ip != "0.0.0.0":
                            origins.add(f"http://{gateway_ip}:{port}")
                        break
        except Exception:
            pass
        
        # Environment-specific origins
        env_host = os.environ.get('EXTERNAL_HOST')
        if env_host:
            origins.add(f"http://{env_host}:{port}")
            origins.add(f"https://{env_host}:{port}")
        
        # Convert to list and add wildcard as fallback for production
        origins_list = list(origins)
        
        # For production, also allow wildcard to ensure compatibility
        if self.environment.lower() == "production":
            origins_list.append("*")
        
        return origins_list if origins_list else ["*"]
    
    # File Storage
    media_root: str = Field(default="./media", description="Media files root directory")
    poster_cache_dir: str = Field(default="./cache/posters", description="Poster cache directory")
    temp_dir: str = Field(default="./tmp", description="Temporary files directory")
    
    # External APIs
    jellyfin_url: Optional[str] = Field(default=None, description="Jellyfin server URL")
    jellyfin_api_key: Optional[str] = Field(default=None, description="Jellyfin API key")
    jellyfin_user_id: Optional[str] = Field(default=None, description="Jellyfin user ID")
    
    # Logging
    log_level: str = Field(default="DEBUG", description="Log level")
    log_format: str = Field(default="json", description="Log format (json/console)")
    log_file_path: str = Field(default="./logs/aphrodite-v2.log", description="Log file path")
    log_max_size: str = Field(default="10MB", description="Log file max size")
    log_backup_count: int = Field(default=5, description="Log backup count")
    
    # Feature Flags
    enable_background_jobs: bool = Field(default=True, description="Enable background job processing")
    enable_websockets: bool = Field(default=True, description="Enable WebSocket support")
    enable_metrics: bool = Field(default=True, description="Enable metrics collection")
    enable_debug_toolbar: bool = Field(default=True, description="Enable debug toolbar")
    
    # Monitoring
    monitoring_port: int = Field(default=8080, description="Monitoring dashboard port")
    health_check_interval: int = Field(default=30, description="Health check interval in seconds")
    metrics_enabled: bool = Field(default=True, description="Enable metrics collection")
    
    # Processing
    max_concurrent_jobs: int = Field(default=4, description="Maximum concurrent processing jobs")
    job_timeout: int = Field(default=300, description="Job timeout in seconds")
    image_quality: int = Field(default=95, description="Image quality for processed posters")
    max_image_size: tuple = Field(default=(2000, 3000), description="Maximum image dimensions")
    
    model_config = SettingsConfigDict(
        env_file=[".env", ".env.docker", ".env.development"],
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

def get_database_url() -> str:
    """Get database URL with fallback"""
    settings = get_settings()
    return settings.database_url

def get_redis_url() -> str:
    """Get Redis URL with fallback"""
    settings = get_settings()
    return settings.redis_url

def is_development() -> bool:
    """Check if running in development environment"""
    settings = get_settings()
    return settings.environment.lower() in ["development", "dev"]

def is_production() -> bool:
    """Check if running in production environment"""
    settings = get_settings()
    return settings.environment.lower() in ["production", "prod"]

def is_testing() -> bool:
    """Check if running in testing environment"""
    settings = get_settings()
    return settings.environment.lower() in ["testing", "test"]
