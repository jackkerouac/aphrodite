"""
Application Configuration Management

Centralized configuration using Pydantic Settings with environment variable support.
"""

import os
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
    
    # Host validation - simple string field that we'll parse in the app
    allowed_hosts: str = Field(
        default="*",
        description="Allowed host headers (comma-separated or *)"
    )
    
    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://aphrodite:development@localhost:5433/aphrodite_v2",
        description="Database connection URL"
    )
    database_pool_size: int = Field(default=20, description="Database connection pool size")
    database_max_overflow: int = Field(default=30, description="Database max overflow connections")
    
    # Redis
    redis_url: str = Field(
        default="redis://localhost:6380/0",
        description="Redis connection URL"
    )
    redis_max_connections: int = Field(default=20, description="Redis max connections")
    
    # Celery
    celery_broker_url: str = Field(
        default="redis://localhost:6380/0",
        description="Celery broker URL"
    )
    celery_result_backend: str = Field(
        default="redis://localhost:6380/1",
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
        default="http://localhost:3000,http://127.0.0.1:3000",
        description="Allowed CORS origins (comma-separated or *)"
    )
    
    # Helper methods to parse string fields into lists
    def get_allowed_hosts_list(self) -> List[str]:
        """Get allowed hosts as a list"""
        if self.allowed_hosts == "*":
            return ["*"]
        return [host.strip() for host in self.allowed_hosts.split(',') if host.strip()]
    
    def get_cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list"""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(',') if origin.strip()]
    
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
        env_file=".env.development",
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
