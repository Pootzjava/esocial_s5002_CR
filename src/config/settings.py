"""
Configurações da aplicação usando Pydantic Settings.
Carrega variáveis de ambiente do arquivo .env ou do sistema.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Configurações da aplicação."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Aplicação
    APP_NAME: str = "eSocial Rendimentos SaaS"
    APP_VERSION: str = "3.0.0-enterprise"
    DEBUG: bool = False
    
    # Banco de Dados
    DATABASE_URL: str = "sqlite:///./esocial_saas.db"
    
    # JWT
    JWT_SECRET_KEY: str = "sua-chave-secreta-muito-forte-e-social-saas-2024"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 horas
    
    # Stripe (Billing)
    STRIPE_SECRET_KEY: str = "sk_test_xxx"
    STRIPE_WEBHOOK_SECRET: str = "whsec_xxx"
    STRIPE_PRODUCT_ID_BASIC: str = "prod_basic"
    STRIPE_PRODUCT_ID_PRO: str = "prod_pro"
    STRIPE_PRODUCT_ID_ENTERPRISE: str = "prod_enterprise"
    
    # CORS
    CORS_ORIGINS: list[str] = ["*"]
    
    # Limites
    MAX_UPLOAD_SIZE_MB: int = 50
    MAX_EMPLOYEES_PER_BATCH: int = 1000
    
    # Audit Log
    AUDIT_LOG_RETENTION_DAYS: int = 365 * 5  # 5 anos (requisito fiscal)
    
    # ERP Integration
    ERP_MAX_FILE_SIZE_MB: int = 50


@lru_cache()
def get_settings() -> Settings:
    """Retorna instância singleton de configurações."""
    return Settings()


# Instância global para importação direta
settings = get_settings()
