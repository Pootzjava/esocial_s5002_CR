"""
Configuração do Banco de Dados - SQLAlchemy
Fase 1: MVP Core
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# URL do banco de dados (SQLite para desenvolvimento, PostgreSQL para produção)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./esocial_saas.db"
)

# Configurar engine
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(DATABASE_URL, connect_args=connect_args)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class para modelos
Base = declarative_base()


async def init_db():
    """
    Inicializa o banco de dados criando as tabelas
    """
    # Importar todos os modelos ORM para registrar no Base
    from src.domain.models_orm import Tenant, User, Employee, IncomeEvent, PDFDocument, ProcessingJob
    
    # Criar tabelas
    Base.metadata.create_all(bind=engine)


def get_db():
    """
    Dependency para obter sessão do banco de dados
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
