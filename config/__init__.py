"""
eSocial Rendimentos SaaS - Configuration Module
Fase 0: Fundação
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os


class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # Application
    APP_NAME: str = Field(default="eSocial Rendimentos SaaS")
    APP_VERSION: str = Field(default="0.1.0")
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=False)
    
    # Server
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/esocial_saas"
    )
    DATABASE_POOL_SIZE: int = Field(default=10)
    DATABASE_MAX_OVERFLOW: int = Field(default=20)
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    
    # Security
    SECRET_KEY: str = Field(
        default="change-this-secret-key-in-production-min-32-chars-xyz"
    )
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)
    
    # Multi-tenancy
    TENANT_HEADER: str = Field(default="X-Tenant-ID")
    DEFAULT_TENANT: str = Field(default="default")
    
    # Storage
    STORAGE_TYPE: str = Field(default="local")
    STORAGE_PATH: str = Field(default="/tmp/esocial-storage")
    MAX_UPLOAD_SIZE_MB: int = Field(default=50)
    
    # eSocial
    ESOCIAL_VERSION: str = Field(default="S-1.3")
    ESOCIAL_AMBIENTE: str = Field(default="PRODUCAO")
    
    # PDF Generation
    PDF_GENERATOR: str = Field(default="reportlab")
    PDF_WATERMARK: bool = Field(default=False)
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FORMAT: str = Field(default="json")
    
    # Monitoring
    PROMETHEUS_ENABLED: bool = Field(default=True)
    METRICS_PATH: str = Field(default="/metrics")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=60)
    
    # Celery
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/1")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/2")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Singleton instance
settings = Settings()


def get_settings() -> Settings:
    """Retorna as configurações da aplicação"""
    return settings
