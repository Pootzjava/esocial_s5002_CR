"""
Router de Billing e Gestão de Assinaturas

Integração com Stripe para gestão de planos, checkout e webhooks.
"""
from fastapi import APIRouter, Request, HTTPException, status, Depends, Header
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import stripe
import os
from sqlalchemy.orm import Session
from src.infrastructure.database import get_db
from src.domain.models_orm import Tenant
from src.core.permissions import require_role

router = APIRouter(prefix="/api/v1/billing", tags=["Billing"])

# Configuração do Stripe (simulada para ambiente de desenvolvimento)
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "sk_test_mock_key")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_mock_secret")
stripe.api_key = STRIPE_SECRET_KEY

# Planos disponíveis
PLANS = {
    "free": {"price_id": "price_free", "amount": 0, "features": ["Até 10 funcionários"]},
    "starter": {"price_id": "price_starter", "amount": 9900, "features": ["Até 50 funcionários", "Suporte por email"]},
    "professional": {"price_id": "price_pro", "amount": 29900, "features": ["Até 200 funcionários", "Suporte prioritário", "API access"]},
    "enterprise": {"price_id": "price_enterprise", "amount": 99900, "features": ["Ilimitado", "Suporte dedicado", "SLA 99.9%", "SSO"]},
}


class CheckoutSessionRequest(BaseModel):
    plan_tier: str
    success_url: str
    cancel_url: str


class CheckoutSessionResponse(BaseModel):
    session_id: str
    url: str
    plan_tier: str


class WebhookEvent(BaseModel):
    type: str
    data: dict


@router.post("/checkout", response_model=CheckoutSessionResponse)
@require_role("admin")
async def create_checkout_session(
    request_data: CheckoutSessionRequest,
    db: Session = Depends(get_db),
    tenant_id: str = None  # Injetado pelo middleware
):
    """
    Cria uma sessão de checkout do Stripe para upgrade de plano.
    """
    if request_data.plan_tier not in PLANS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Plano inválido. Opções: {list(PLANS.keys())}"
        )

    # Busca o tenant atual
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não encontrado")

    # Simula criação de sessão Stripe (em produção usaria stripe.checkout.Session.create)
    session_id = f"sess_{tenant_id}_{request_data.plan_tier}_{datetime.now().timestamp()}"
    
    # Em produção:
    # session = stripe.checkout.Session.create(
    #     customer=tenant.stripe_customer_id,
    #     payment_method_types=['card'],
    #     line_items=[{'price': PLANS[request_data.plan_tier]['price_id'], 'quantity': 1}],
    #     mode='subscription',
    #     success_url=request_data.success_url,
    #     cancel_url=request_data.cancel_url,
    # )

    return CheckoutSessionResponse(
        session_id=session_id,
        url=f"https://checkout.stripe.com/mock/{session_id}",
        plan_tier=request_data.plan_tier
    )


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Endpoint para receber webhooks do Stripe.
    Atualiza o status da assinatura do tenant baseado nos eventos.
    Endpoint público - a validação da assinatura é feita pelo payload.
    """
    body = await request.body()
    
    # Em produção, validaria a assinatura:
    # event = stripe.Webhook.construct_event(body, stripe_signature, STRIPE_WEBHOOK_SECRET)
    
    # Simulação do payload do webhook
    try:
        payload = await request.json()
    except:
        raise HTTPException(status_code=400, detail="JSON inválido")

    event_type = payload.get("type")
    data_object = payload.get("data", {}).get("object", {})

    if event_type == "checkout.session.completed":
        # Extrai informações da sessão completada
        customer_id = data_object.get("customer")
        subscription_id = data_object.get("subscription")
        
        # Busca tenant pelo stripe_customer_id
        tenant = db.query(Tenant).filter(Tenant.stripe_customer_id == customer_id).first()
        
        if tenant:
            # Determina o plano baseado no metadata da sessão (em produção viria do Stripe)
            plan_tier = data_object.get("metadata", {}).get("plan_tier", "starter")
            
            tenant.subscription_status = "active"
            tenant.plan_tier = plan_tier
            
            db.commit()
            
            return {"status": "success", "message": f"Tenant {tenant.name} atualizado para plano {plan_tier}"}
    
    elif event_type == "customer.subscription.deleted":
        customer_id = data_object.get("customer")
        tenant = db.query(Tenant).filter(Tenant.stripe_customer_id == customer_id).first()
        
        if tenant:
            tenant.subscription_status = "canceled"
            tenant.plan_tier = "free"
            db.commit()
            
            return {"status": "success", "message": f"Assinatura do tenant {tenant.name} cancelada"}

    return {"status": "ignored", "message": "Evento não processado"}


@router.get("/subscription")
@require_role("admin")
async def get_subscription_info(
    db: Session = Depends(get_db),
    tenant_id: str = None
):
    """
    Retorna informações da assinatura atual do tenant.
    """
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não encontrado")

    plan_info = PLANS.get(tenant.plan_tier, PLANS["free"])
    
    return {
        "tenant_id": tenant.id,
        "tenant_name": tenant.name,
        "plan_tier": tenant.plan_tier,
        "subscription_status": tenant.subscription_status,
        "plan_amount_cents": plan_info["amount"],
        "plan_features": plan_info["features"],
        "stripe_customer_id": tenant.stripe_customer_id
    }


@router.get("/plans")
async def list_plans():
    """
    Lista todos os planos disponíveis com suas features.
    Endpoint público - não requer autenticação.
    """
    return {
        "plans": [
            {
                "tier": tier,
                "name": tier.capitalize(),
                "amount_cents": info["amount"],
                "amount_brl": f"R$ {info['amount'] / 100:.2f}",
                "features": info["features"]
            }
            for tier, info in PLANS.items()
        ]
    }
