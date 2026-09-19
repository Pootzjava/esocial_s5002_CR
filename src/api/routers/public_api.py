"""
eSocial Rendimentos SaaS - Developer Portal & Public API Router
Fase 6: Ecosystem - APIs Públicas para Parceiros e Desenvolvedores
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import hashlib
import hmac
import json

router = APIRouter(prefix="/api/v1/public", tags=["Public API"])

# Modelos de Request/Response
class WebhookSubscription(BaseModel):
    url: str = Field(..., description="URL endpoint para receber webhooks")
    events: List[str] = Field(..., description="Lista de eventos para subscrição")
    secret: Optional[str] = Field(None, description="Secret para assinatura HMAC")

class WebhookEvent(BaseModel):
    id: str
    type: str
    timestamp: datetime
    data: dict
    tenant_id: str

class APIKeyResponse(BaseModel):
    api_key: str
    key_name: str
    created_at: datetime
    expires_at: Optional[datetime]
    permissions: List[str]

class RateLimitInfo(BaseModel):
    limit: int
    remaining: int
    reset_at: datetime

# Simulação de banco de dados de API Keys e Webhooks
api_keys_db = {}
webhooks_db = {}

@router.get("/docs", summary="Documentação da API Pública")
async def get_api_docs():
    """
    Retorna documentação completa da API pública para desenvolvedores.
    Inclui exemplos de código, schemas e endpoints disponíveis.
    """
    return {
        "title": "eSocial Rendimentos SaaS - Public API",
        "version": "1.0.0",
        "base_url": "/api/v1/public",
        "authentication": "API Key via header X-API-Key",
        "rate_limits": {
            "free_tier": "100 requests/hour",
            "pro_tier": "1000 requests/hour",
            "enterprise_tier": "10000 requests/hour"
        },
        "endpoints": [
            {
                "path": "/employees",
                "method": "GET",
                "description": "Listar funcionários da empresa",
                "parameters": ["limit", "offset", "search"]
            },
            {
                "path": "/income-events",
                "method": "GET", 
                "description": "Listar eventos de rendimento",
                "parameters": ["employee_id", "year", "month"]
            },
            {
                "path": "/pdf/generate",
                "method": "POST",
                "description": "Gerar comprovante de rendimentos em PDF",
                "body": ["employee_ids", "template_id"]
            },
            {
                "path": "/webhooks",
                "method": "POST",
                "description": "Configurar webhooks para eventos",
                "body": ["url", "events", "secret"]
            }
        ],
        "code_examples": {
            "python": "sdk-examples/python/example.py",
            "nodejs": "sdk-examples/nodejs/example.js",
            "curl": "docs/developer-portal/curl-examples.md"
        }
    }

@router.post("/api-keys", response_model=APIKeyResponse, summary="Criar API Key")
async def create_api_key(
    key_name: str = Body(..., description="Nome descritivo da chave"),
    permissions: List[str] = Body(["read:employees", "read:events"], description="Permissões da chave"),
    expires_in_days: Optional[int] = Body(None, description="Dias até expiração")
):
    """
    Cria uma nova API Key para acesso à API pública.
    
    **Permissões disponíveis:**
    - read:employees
    - read:events
    - write:pdf
    - manage:webhooks
    
    **Expira em:** Opcional, padrão é não expirar.
    """
    import secrets
    from datetime import timedelta
    
    api_key = f"esr_{secrets.token_urlsafe(32)}"
    key_id = hashlib.sha256(api_key.encode()).hexdigest()[:16]
    
    expires_at = None
    if expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
    
    api_keys_db[key_id] = {
        "api_key": api_key,
        "key_name": key_name,
        "created_at": datetime.utcnow(),
        "expires_at": expires_at,
        "permissions": permissions,
        "active": True,
        "usage_count": 0
    }
    
    return APIKeyResponse(
        api_key=api_key,
        key_name=key_name,
        created_at=datetime.utcnow(),
        expires_at=expires_at,
        permissions=permissions
    )

@router.get("/api-keys/{key_id}", summary="Obter informações da API Key")
async def get_api_key_info(key_id: str):
    """Retorna informações sobre uma API Key específica (sem revelar a chave secreta)."""
    if key_id not in api_keys_db:
        raise HTTPException(status_code=404, detail="API Key não encontrada")
    
    key_data = api_keys_db[key_id]
    return {
        "key_id": key_id,
        "key_name": key_data["key_name"],
        "created_at": key_data["created_at"],
        "expires_at": key_data["expires_at"],
        "permissions": key_data["permissions"],
        "active": key_data["active"],
        "usage_count": key_data["usage_count"]
    }

@router.delete("/api-keys/{key_id}", summary="Revogar API Key")
async def revoke_api_key(key_id: str):
    """Revoga uma API Key, tornando-a imediatamente inválida."""
    if key_id not in api_keys_db:
        raise HTTPException(status_code=404, detail="API Key não encontrada")
    
    api_keys_db[key_id]["active"] = False
    return {"message": "API Key revogada com sucesso", "key_id": key_id}

@router.post("/webhooks", summary="Configurar Webhook")
async def create_webhook(subscription: WebhookSubscription):
    """
    Configura um webhook para receber notificações de eventos.
    
    **Eventos disponíveis:**
    - employee.created
    - employee.updated
    - income_event.created
    - pdf.generated
    - processing.completed
    
    **Segurança:** Recomenda-se usar o secret para validar assinaturas HMAC.
    """
    webhook_id = hashlib.sha256(f"{subscription.url}{datetime.utcnow()}".encode()).hexdigest()[:16]
    
    webhooks_db[webhook_id] = {
        "url": subscription.url,
        "events": subscription.events,
        "secret": subscription.secret or hashlib.sha256(f"{webhook_id}".encode()).hexdigest(),
        "created_at": datetime.utcnow(),
        "active": True,
        "last_triggered": None,
        "success_count": 0,
        "failure_count": 0
    }
    
    return {
        "webhook_id": webhook_id,
        "url": subscription.url,
        "events": subscription.events,
        "secret": webhooks_db[webhook_id]["secret"],
        "created_at": webhooks_db[webhook_id]["created_at"],
        "status": "active"
    }

@router.get("/webhooks", summary="Listar Webhooks")
async def list_webhooks():
    """Lista todos os webhooks configurados."""
    return [
        {
            "webhook_id": wid,
            "url": wdata["url"],
            "events": wdata["events"],
            "active": wdata["active"],
            "created_at": wdata["created_at"],
            "last_triggered": wdata["last_triggered"]
        }
        for wid, wdata in webhooks_db.items()
    ]

@router.delete("/webhooks/{webhook_id}", summary="Remover Webhook")
async def delete_webhook(webhook_id: str):
    """Remove um webhook configurado."""
    if webhook_id not in webhooks_db:
        raise HTTPException(status_code=404, detail="Webhook não encontrado")
    
    del webhooks_db[webhook_id]
    return {"message": "Webhook removido com sucesso", "webhook_id": webhook_id}

@router.get("/rate-limit", response_model=RateLimitInfo, summary="Verificar Rate Limit")
async def get_rate_limit_info(
    api_key: str = Query(..., description="API Key para verificar limites")
):
    """Retorna informações sobre o rate limit atual da API Key."""
    key_id = hashlib.sha256(api_key.encode()).hexdigest()[:16]
    
    if key_id not in api_keys_db:
        raise HTTPException(status_code=404, detail="API Key não encontrada")
    
    # Simulação de rate limit
    return RateLimitInfo(
        limit=1000,
        remaining=847,
        reset_at=datetime.utcnow()
    )

@router.get("/health", summary="Health Check da API Pública")
async def public_api_health():
    """Verifica saúde da API pública."""
    return {
        "status": "healthy",
        "service": "public-api",
        "version": "1.0.0",
        "timestamp": datetime.utcnow()
    }
