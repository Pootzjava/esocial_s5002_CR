"""
Testes de integração para Audit Log (Fase 3: Enterprise Ready).
Testa criação, consulta e exportação de logs de auditoria.
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from src.api.main import app
from src.infrastructure.database import get_db, engine
from src.domain.models_orm import Tenant, User, AuditLog, UserRole
from sqlalchemy.orm import sessionmaker
import json

client = TestClient(app)

# Configurar banco de dados de teste
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Cria sessão de banco de dados para testes."""
    # Criar tabelas
    from src.domain.models_orm import Base
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Limpar banco após teste
        from src.domain.models_orm import Base
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_tenant(db_session):
    """Cria tenant de teste."""
    tenant = Tenant(
        name="Empresa Teste LTDA",
        cnpj="12.345.678/0001-90",
        email="contato@empresateste.com.br",
        plan_tier="enterprise",
        subscription_status="active",
    )
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    return tenant


@pytest.fixture(scope="function")
def test_user(db_session, test_tenant):
    """Cria usuário admin de teste."""
    user = User(
        tenant_id=test_tenant.id,
        username="admin_teste",
        email="admin@empresateste.com.br",
        hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.G2YDLwzYebjEOi",  # "password123"
        role=UserRole.admin,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def auth_token(test_user):
    """Realiza login e retorna token JWT."""
    response = client.post("/api/v1/auth/login", json={
        "username": test_user.username,
        "password": "password123"
    })
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def sample_audit_logs(db_session, test_tenant, test_user):
    """Cria logs de auditoria de exemplo."""
    logs = []
    for i in range(5):
        log = AuditLog(
            user_id=test_user.id,
            tenant_id=test_tenant.id,
            action="VIEW" if i % 2 == 0 else "CREATE",
            resource_type="Employee" if i % 2 == 0 else "PDFDocument",
            resource_id=100 + i,
            details={"extra_info": f"log_{i}"},
            ip_address=f"192.168.1.{i}",
            user_agent="TestAgent/1.0",
        )
        db_session.add(log)
        logs.append(log)
    
    db_session.commit()
    return logs


class TestAuditLogEndpoints:
    """Testes para endpoints de Audit Log."""

    def test_get_audit_logs_success(self, auth_token, sample_audit_logs):
        """Testa recuperação de logs com sucesso."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = client.get("/api/v1/audit/logs", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "logs" in data
        assert data["total"] >= 5
        assert len(data["logs"]) > 0
        
        # Verificar estrutura do log
        first_log = data["logs"][0]
        assert "action" in first_log
        assert "resource_type" in first_log
        assert "created_at" in first_log

    def test_get_audit_logs_with_filters(self, auth_token, sample_audit_logs, db_session, test_tenant):
        """Testa filtros de logs."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Filtrar por ação
        response = client.get("/api/v1/audit/logs?action=VIEW", headers=headers)
        assert response.status_code == 200
        data = response.json()
        # Todos os logs retornados devem ser VIEW
        for log in data["logs"]:
            assert log["action"] == "VIEW"

    def test_get_audit_logs_pagination(self, auth_token, sample_audit_logs):
        """Testa paginação de logs."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = client.get("/api/v1/audit/logs?limit=2&offset=0", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["logs"]) <= 2
        assert data["limit"] == 2
        assert data["offset"] == 0

    def test_export_audit_logs_csv(self, auth_token, sample_audit_logs):
        """Testa exportação de logs em CSV."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = client.get("/api/v1/audit/logs/export", headers=headers)
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert "attachment; filename=audit_logs.csv" in response.headers["content-disposition"]
        
        # Verificar conteúdo CSV
        content = response.content.decode('utf-8')
        assert "id,user_id,tenant_id,action,resource_type" in content

    def test_get_audit_logs_unauthorized(self):
        """Testa acesso sem autenticação."""
        response = client.get("/api/v1/audit/logs")
        assert response.status_code in [401, 403]

    def test_get_audit_logs_different_tenant(self, db_session, auth_token):
        """Testa que usuário só vê logs do seu tenant."""
        # Criar outro tenant
        other_tenant = Tenant(
            name="Outra Empresa",
            cnpj="98.765.432/0001-10",
            email="outra@empresa.com.br",
            plan_tier="basic",
        )
        db_session.add(other_tenant)
        db_session.commit()
        
        # Criar logs no outro tenant
        other_user = User(
            tenant_id=other_tenant.id,
            email="user@outraempresa.com.br",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.G2YDLwzYebjEOi",
            name="Outro Usuário",
            role="admin",
        )
        db_session.add(other_user)
        db_session.commit()
        
        other_log = AuditLog(
            user_id=other_user.id,
            tenant_id=other_tenant.id,
            action="DELETE",
            resource_type="Employee",
            resource_id=999,
            details={"should_not_appear": True},
        )
        db_session.add(other_log)
        db_session.commit()
        
        # Buscar logs do tenant original
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = client.get("/api/v1/audit/logs", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Garantir que logs do outro tenant não aparecem
        for log in data["logs"]:
            assert log.get("resource_id") != 999


class TestAuditLogService:
    """Testes unitários para AuditLogService."""

    def test_log_action_creates_log(self, db_session, test_tenant, test_user):
        """Testa criação de log de auditoria."""
        from src.services.audit_log import AuditLogService
        
        log = AuditLogService.log_action(
            db=db_session,
            user_id=test_user.id,
            tenant_id=test_tenant.id,
            action="LOGIN",
            resource_type="User",
            ip_address="192.168.1.100",
        )
        
        assert log.id is not None
        assert log.action == "LOGIN"
        assert log.created_at is not None

    def test_get_logs_by_tenant_filtering(self, db_session, test_tenant, test_user, sample_audit_logs):
        """Testa filtragem de logs por tenant."""
        from src.services.audit_log import AuditLogService
        
        logs = AuditLogService.get_logs_by_tenant(
            db=db_session,
            tenant_id=test_tenant.id,
            limit=10,
        )
        
        assert len(logs) >= 5
        # Todos os logs devem pertencer ao tenant
        for log in logs:
            assert log.tenant_id == test_tenant.id
