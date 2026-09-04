"""
Database Configuration and Session Management
Fase 0: Fundação

Módulo responsável pela configuração do banco de dados e gerenciamento de sessões.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import logging

from config import settings

logger = logging.getLogger(__name__)

# Criar engine do banco de dados
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,  # Verifica conexões antes de usar
    echo=settings.DEBUG,  # Log SQL em debug mode
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos ORM
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency para obter sessão do banco de dados.
    
    Usage:
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Inicializa o banco de dados criando todas as tabelas.
    Deve ser chamado apenas em ambiente de desenvolvimento/teste.
    """
    logger.info("Inicializando banco de dados...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Tabelas criadas com sucesso!")
    except Exception as e:
        logger.error(f"Erro ao criar tabelas: {e}")
        raise


def drop_db() -> None:
    """
    Remove todas as tabelas do banco de dados.
    CUIDADO: Isso apaga todos os dados!
    """
    logger.warning("Removendo todas as tabelas do banco de dados...")
    try:
        Base.metadata.drop_all(bind=engine)
        logger.warning("Tabelas removidas!")
    except Exception as e:
        logger.error(f"Erro ao remover tabelas: {e}")
        raise
