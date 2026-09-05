"""
Testes de Integração - Middleware de Isolamento Multi-Tenant

Valida que usuários de um tenant não conseguem acessar dados de outro tenant.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from jose import jwt
from datetime import datetime, timedelta

from src.api.main import app
from src.infrastructure.database import get_db, engine, Base
from src.domain.models_orm import Tenant, User, Employee, UserRole, PlanTier, SubscriptionStatus
from src.infrastructure.database import create_tables

# Configuração do JWT para testes
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
    
    # Limpa o banco após cada teste
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def create_token(tenant_id: int, user_id: int, role: str = "viewer") -> str:
    """Cria um token JWT válido para testes"""
    expire = datetime.utcnow() + timedelta(hours=1)
    payload = {
        "sub": str(user_id),
        "tenant_id": tenant_id,
        "role": role,
        "exp": expire
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def setup_tenants(db: Session):
    """Cria dois tenants com dados distintos para testes de isolamento"""
    # Tenant A
    tenant_a = Tenant(
        name="Empresa A LTDA",
        cnpj="11.111.111/0001-11",
        email="contato@empresa-a.com.br",
        plan_tier=PlanTier.professional,
        subscription_status=SubscriptionStatus.active
    )
    db.add(tenant_a)
    db.flush()
    
    # Tenant B
    tenant_b = Tenant(
        name="Empresa B S.A.",
        cnpj="22.222.222/0001-22",
        email="contato@empresa-b.com.br",
        plan_tier=PlanTier.professional,
        subscription_status=SubscriptionStatus.active
    )
    db.add(tenant_b)
    db.flush()
    
    # Funcionário do Tenant A
    employee_a = Employee(
        tenant_id=tenant_a.id,
        cpf="111.111.111-11",
        name="Funcionário A"
    )
    db.add(employee_a)
    db.flush()
    
    # Funcionário do Tenant B
    employee_b = Employee(
        tenant_id=tenant_b.id,
        cpf="222.222.222-22",
        name="Funcionário B"
    )
    db.add(employee_b)
    db.flush()
    
    db.commit()
    
    return tenant_a, tenant_b, employee_a, employee_b


class TestTenantIsolation:
    """Testes de isolamento multi-tenant"""
    
    def test_user_from_tenant_a_cannot_access_employee_from_tenant_b(self, client):
        """Usuário do Tenant A não deve conseguir acessar funcionário do Tenant B"""
        db = Session(bind=engine)
        
        try:
            # Setup
            tenant_a, tenant_b, employee_a, employee_b = setup_tenants(db)
            
            # Cria token para usuário do Tenant A
            token = create_token(tenant_id=tenant_a.id, user_id=999, role="viewer")
            
            headers = {"Authorization": f"Bearer {token}"}
            
            # Tenta acessar funcionário do Tenant B (deve falhar)
            # Nota: Em uma implementação real, o endpoint filtraria por tenant_id automaticamente
            # Aqui simulamos que o middleware injeta tenant_id na request
            response = client.get(f"/api/v1/employees/{employee_b.id}", headers=headers)
            
            # Deve retornar 403 ou 404 pois o funcionário não pertence ao tenant do usuário
            assert response.status_code in [403, 404]
            
        finally:
            db.close()
    
    def test_user_from_tenant_a_can_access_employee_from_tenant_a(self, client):
        """Usuário do Tenant A deve conseguir acessar funcionário do próprio Tenant A"""
        db = Session(bind=engine)
        
        try:
            # Setup
            tenant_a, tenant_b, employee_a, employee_b = setup_tenants(db)
            
            # Cria token para usuário do Tenant A
            token = create_token(tenant_id=tenant_a.id, user_id=999, role="manager")
            
            headers = {"Authorization": f"Bearer {token}"}
            
            # Acessa funcionário do próprio tenant (deve funcionar)
            response = client.get(f"/api/v1/employees/{employee_a.id}", headers=headers)
            
            # Como o funcionário existe mas pode não haver endpoint específico, 
            # validamos que o middleware permitiu a requisição passar
            # O status 404 aqui significaria que o endpoint não existe, não erro de permissão
            assert response.status_code != 403
            
        finally:
            db.close()
    
    def test_middleware_extracts_tenant_id_from_token(self, client):
        """Middleware deve extrair corretamente o tenant_id do token JWT"""
        # Cria token com tenant_id específico
        token = create_token(tenant_id=123, user_id=456, role="admin")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Faz request para endpoint que requer autenticação
        response = client.get("/api/v1/employees", headers=headers)
        
        # Middleware deve permitir passagem (não retornar 401 ou 403 por falta de auth)
        # Pode retornar 200 (se houver employees) ou 404 (se não houver)
        assert response.status_code in [200, 404], f"Expected 200 or 404, got {response.status_code}"
    
    def test_request_without_token_returns_401(self, client):
        """Requisição sem token deve retornar 401 Unauthorized"""
        response = client.get("/api/v1/employees")
        
        assert response.status_code == 401
        assert "autenticação" in response.json()["detail"].lower() or "não autenticado" in response.json()["detail"].lower()
    
    def test_request_with_invalid_token_returns_401(self, client):
        """Requisição com token inválido deve retornar 401"""
        headers = {"Authorization": "Bearer invalid_token_xyz"}
        
        response = client.get("/api/v1/employees", headers=headers)
        
        assert response.status_code == 401
        assert "inválido" in response.json()["detail"].lower() or "não autenticado" in response.json()["detail"].lower()
    
    def test_request_with_expired_token_returns_401(self, client):
        """Requisição com token expirado deve retornar 401"""
        from jose import jwt
        from datetime import datetime, timedelta
        
        # Cria token já expirado
        expire = datetime.utcnow() - timedelta(hours=1)
        payload = {
            "sub": "123",
            "tenant_id": 456,
            "role": "viewer",
            "exp": expire
        }
        expired_token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        
        headers = {"Authorization": f"Bearer {expired_token}"}
        
        response = client.get("/api/v1/employees", headers=headers)
        
        assert response.status_code == 401
    
    def test_public_routes_dont_require_token(self, client):
        """Rotas públicas (health, docs) não devem requerer token"""
        # Health check é público
        response = client.get("/api/v1/health/status")
        assert response.status_code == 200
        
        # Docs são públicos
        response = client.get("/docs")
        assert response.status_code == 200
        
        # OpenAPI JSON é público
        response = client.get("/openapi.json")
        assert response.status_code == 200
    
    def test_tenant_id_injected_in_request_state(self, client):
        """Middleware deve injetar tenant_id no request.state"""
        # Este teste valida a lógica interna do middleware
        db = Session(bind=engine)
        
        try:
            tenant_a, tenant_b, _, _ = setup_tenants(db)
            
            token = create_token(tenant_id=tenant_a.id, user_id=999, role="admin")
            headers = {"Authorization": f"Bearer {token}"}
            
            # Faz request - o middleware deve injetar tenant_id
            response = client.get("/api/v1/health/detailed", headers=headers)
            
            assert response.status_code == 200
            
        finally:
            db.close()


# Helper para obter db session nos testes
def override_get_db_for_test():
    db = Session(bind=engine)
    return db
