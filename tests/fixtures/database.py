"""
Database Fixtures for Tests
Fase 0: Fundação

Fixtures para configuração do banco de dados em testes.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from infrastructure.database import Base, get_db
from domain.models_orm import Tenant, Usuario


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
def db_client(db_session):
    """
    Fixture que simula o dependency injection do FastAPI.
    Usage: def test_something(db_client): ...
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    return override_get_db


@pytest.fixture
def tenant_fixture(db_session) -> Tenant:
    """Cria um tenant de teste"""
    tenant = Tenant(
        nome="Empresa Teste Ltda",
        cnpj="12345678000190",
        slug="empresa-teste",
        ativo=True,
        plano="professional",
    )
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    return tenant


@pytest.fixture
def admin_user_fixture(db_session, tenant_fixture) -> Usuario:
    """Cria um usuário admin de teste"""
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    usuario = Usuario(
        tenant_id=tenant_fixture.id,
        email="admin@empresateste.com.br",
        senha_hash=pwd_context.hash("senha123"),
        nome="Admin Teste",
        ativo=True,
        eh_admin=True,
    )
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)
    return usuario
