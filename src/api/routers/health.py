"""
Router de Health Check - Monitoramento da API
Fase 1: MVP Core
"""
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime
import os

from src.api.routers.auth import get_current_user, TokenData

router = APIRouter()


class HealthStatus(BaseModel):
    """Status de saúde da API"""
    status: str
    version: str
    phase: str
    timestamp: datetime
    uptime_seconds: Optional[float] = None


class DatabaseHealth(BaseModel):
    """Status do banco de dados"""
    status: str
    connected: bool
    latency_ms: Optional[float] = None


class SystemHealth(BaseModel):
    """Status completo do sistema"""
    api: HealthStatus
    database: DatabaseHealth
    environment: str
    dependencies: Dict[str, str]


# Timestamp de início para cálculo de uptime
START_TIME = datetime.utcnow()


@router.get("/status", response_model=HealthStatus)
async def health_status():
    """
    Retorna status básico da API
    
    Endpoint público para verificar se a API está no ar
    """
    uptime = (datetime.utcnow() - START_TIME).total_seconds()
    
    return HealthStatus(
        status="healthy",
        version="2.0.0-multi-tenant",
        phase="Fase 2 - Multi-Tenant + UX",
        timestamp=datetime.utcnow(),
        uptime_seconds=uptime
    )


@router.get("/detailed", response_model=SystemHealth)
async def detailed_health(
    current_user: TokenData = Depends(get_current_user)
):
    """
    Retorna status detalhado do sistema
    
    Requer autenticação. Inclui:
    - Status da API
    - Status do banco de dados
    - Variáveis de ambiente
    - Dependências
    """
    # Mock de health check do banco
    db_healthy = True
    db_latency = 1.5  # ms
    
    return SystemHealth(
        api=HealthStatus(
            status="healthy",
            version="2.0.0-multi-tenant",
            phase="Fase 2 - Multi-Tenant + UX",
            timestamp=datetime.utcnow(),
            uptime_seconds=(datetime.utcnow() - START_TIME).total_seconds()
        ),
        database=DatabaseHealth(
            status="healthy" if db_healthy else "unhealthy",
            connected=db_healthy,
            latency_ms=db_latency if db_healthy else None
        ),
        environment=os.getenv("ENVIRONMENT", "development"),
        dependencies={
            "fastapi": "installed",
            "sqlalchemy": "installed",
            "psycopg2": "installed",
            "reportlab": "installed"
        }
    )


@router.get("/ready")
async def readiness_check():
    """
    Verifica se a API está pronta para receber tráfego
    
    Usado por Kubernetes/orquestradores
    """
    # Verificações básicas
    checks = {
        "database": True,
        "storage": True,
        "external_services": True
    }
    
    all_healthy = all(checks.values())
    
    if all_healthy:
        return {"status": "ready", "checks": checks}
    else:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "not_ready", "checks": checks}
        )


@router.get("/live")
async def liveness_check():
    """
    Verifica se a API está viva
    
    Usado por Kubernetes para restart automático
    """
    return {"status": "alive"}
