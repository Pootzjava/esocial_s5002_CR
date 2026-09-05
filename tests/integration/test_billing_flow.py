"""
Testes de Integração - Fluxo de Billing e Assinaturas

Valida o ciclo de vida completo de uma assinatura: criação, pagamento, cancelamento.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt

from src.api.main import app
from src.infrastructure.database import get_db, engine, Base
from src.domain.models_orm import Tenant, User, PlanTier, SubscriptionStatus
from src.infrastructure.database import create_tables

JWT_SECRET = "test_secret_key"
JWT_ALGORITHM = "HS256"


@pytest.fixture(scope="function")
def client():
    """Cria um cliente de teste com banco de dados isolado"""
    create_tables()
    
    def override_get_db():
        db = Session(bind=engine)
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def create_admin_token(tenant_id: int) -> str:
    """Cria token JWT para usuário admin"""
    expire = datetime.utcnow() + timedelta(hours=1)
    payload = {
        "sub": "1",
        "tenant_id": tenant_id,
        "role": "admin",
        "exp": expire
    }
    # Usa a mesma chave secreta do middleware
    return jwt.encode(payload, "dev-secret-key-change-in-production", algorithm=JWT_ALGORITHM)


def setup_tenant_with_subscription(db: Session):
    """Cria um tenant com configuração inicial de assinatura"""
    tenant = Tenant(
        name="Teste Empresa Ltda",
        cnpj="33.333.333/0001-33",
        email="teste@empresa.com.br",
        plan_tier=PlanTier.free,
        subscription_status=SubscriptionStatus.trial,
        stripe_customer_id="cus_test123"
    )
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant


class TestBillingFlow:
    """Testes do fluxo de billing e assinaturas"""
    
    def test_create_checkout_session_success(self, client):
        """Testa criação de sessão de checkout para upgrade de plano"""
        db = next(app.dependency_overrides[get_db]())
        
        tenant = setup_tenant_with_subscription(db)
        token = create_admin_token(tenant.id)
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "plan_tier": "professional",
            "success_url": "https://app.example.com/success",
            "cancel_url": "https://app.example.com/cancel"
        }
        
        response = client.post("/api/v1/billing/checkout", json=payload, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "url" in data
        assert data["plan_tier"] == "professional"
        
        db.close()
    
    def test_create_checkout_session_invalid_plan(self, client):
        """Testa erro ao solicitar plano inválido"""
        db = next(app.dependency_overrides[get_db]())
        
        tenant = setup_tenant_with_subscription(db)
        token = create_admin_token(tenant.id)
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "plan_tier": "plano_invalido_xyz",
            "success_url": "https://example.com/success",
            "cancel_url": "https://example.com/cancel"
        }
        
        response = client.post("/api/v1/billing/checkout", json=payload, headers=headers)
        
        assert response.status_code == 400
        assert "Plano inválido" in response.json()["detail"]
        
        db.close()
    
    def test_webhook_checkout_session_completed(self, client):
        """Testa webhook de checkout completado com sucesso"""
        db = next(app.dependency_overrides[get_db]())
        
        tenant = setup_tenant_with_subscription(db)
        tenant.stripe_customer_id = "cus_test123"
        db.commit()
        
        # Simula payload do Stripe
        webhook_payload = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "customer": "cus_test123",
                    "subscription": "sub_test456",
                    "metadata": {
                        "plan_tier": "professional"
                    }
                }
            }
        }
        
        headers = {"Content-Type": "application/json"}
        response = client.post("/api/v1/billing/webhook", json=webhook_payload, headers=headers)
        
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        
        # Verifica se o tenant foi atualizado no banco
        db.refresh(tenant)
        assert tenant.subscription_status == SubscriptionStatus.active
        assert tenant.plan_tier == PlanTier.professional
        
        db.close()
    
    def test_webhook_subscription_deleted(self, client):
        """Testa webhook de cancelamento de assinatura"""
        db = next(app.dependency_overrides[get_db]())
        
        tenant = setup_tenant_with_subscription(db)
        tenant.plan_tier = PlanTier.professional
        tenant.subscription_status = SubscriptionStatus.active
        tenant.stripe_customer_id = "cus_test789"
        db.commit()
        
        # Simula payload de cancelamento
        webhook_payload = {
            "type": "customer.subscription.deleted",
            "data": {
                "object": {
                    "customer": "cus_test789"
                }
            }
        }
        
        headers = {"Content-Type": "application/json"}
        response = client.post("/api/v1/billing/webhook", json=webhook_payload, headers=headers)
        
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        
        # Verifica se o tenant foi atualizado
        db.refresh(tenant)
        assert tenant.subscription_status == SubscriptionStatus.canceled
        assert tenant.plan_tier == PlanTier.free
        
        db.close()
    
    def test_get_subscription_info(self, client):
        """Testa obtenção de informações da assinatura atual"""
        db = next(app.dependency_overrides[get_db]())
        
        tenant = setup_tenant_with_subscription(db)
        token = create_admin_token(tenant.id)
        
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/v1/billing/subscription", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["tenant_id"] == tenant.id
        assert data["tenant_name"] == tenant.name
        assert data["plan_tier"] == "free"
        assert data["subscription_status"] == "trial"
        assert "plan_features" in data
        
        db.close()
    
    def test_list_plans_endpoint(self, client):
        """Testa listagem de planos disponíveis"""
        response = client.get("/api/v1/billing/plans")
        
        assert response.status_code == 200
        data = response.json()
        assert "plans" in data
        assert len(data["plans"]) >= 4  # free, starter, professional, enterprise
        
        # Valida estrutura de cada plano
        for plan in data["plans"]:
            assert "tier" in plan
            assert "name" in plan
            assert "amount_cents" in plan
            assert "amount_brl" in plan
            assert "features" in plan
    
    def test_non_admin_cannot_access_billing(self, client):
        """Testa que usuário não-admin não pode acessar endpoints de billing"""
        db = next(app.dependency_overrides[get_db]())
        
        tenant = setup_tenant_with_subscription(db)
        
        # Cria token com role viewer (não admin) - USA A MESMA CHAVE DO MIDDLEWARE
        expire = datetime.utcnow() + timedelta(hours=1)
        payload = {
            "sub": "2",
            "tenant_id": tenant.id,
            "role": "viewer",
            "exp": expire
        }
        token = jwt.encode(payload, "dev-secret-key-change-in-production", algorithm=JWT_ALGORITHM)
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Tenta acessar endpoint de checkout (requer admin)
        response = client.post(
            "/api/v1/billing/checkout",
            json={"plan_tier": "starter", "success_url": "x", "cancel_url": "y"},
            headers=headers
        )
        
        # Deve retornar 403 Forbidden
        assert response.status_code == 403
        
        db.close()
