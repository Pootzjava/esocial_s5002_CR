"""
Pytest Configuration
Fase 0: Fundação

Configuração base para testes automatizados.
"""

import sys
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Adicionar o diretório raiz ao path para imports
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from infrastructure.database import Base, get_db
from domain.models_orm import Tenant, Usuario
from src.api.main import app


# Engine SQLite em memória para testes rápidos
@pytest.fixture(scope="session")
def test_engine():
    """Cria engine SQLite em memória para testes"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(test_engine) -> Session:
    """
    Cria uma sessão de banco de dados para cada teste.
    Os dados são automaticamente removidos após o teste.
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    SessionLocal = sessionmaker(bind=connection, autoflush=False, autocommit=False)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """
    Cria um cliente de teste FastAPI com banco de dados isolado por teste.
    Override da dependência get_db para usar a sessão de teste.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    # Criar tenant e usuário padrão para testes
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    tenant = Tenant(
        nome="Empresa Teste Ltda",
        cnpj="12345678000190",
        slug="empresa-teste",
        ativo=True,
        plano="professional",
    )
    db_session.add(tenant)
    db_session.commit()
    
    usuario = Usuario(
        tenant_id=tenant.id,
        email="test@example.com",
        senha_hash=pwd_context.hash("securepass123"),
        nome="Test User",
        ativo=True,
        eh_admin=True,
        username="testuser"
    )
    db_session.add(usuario)
    db_session.commit()
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


# Configurações do pytest
# Removido plugins externos para evitar erros de import
# As fixtures são carregadas automaticamente do conftest.py


def pytest_configure(config):
    """Configuração inicial do pytest"""
    config.addinivalue_line(
        "markers",
        "unit: mark test as a unit test",
    )
    config.addinivalue_line(
        "markers",
        "integration: mark test as an integration test",
    )
    config.addinivalue_line(
        "markers",
        "e2e: mark test as an end-to-end test",
    )
    config.addinivalue_line(
        "markers",
        "slow: mark test as slow running",
    )
