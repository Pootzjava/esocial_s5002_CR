"""
Test Fixtures Package
Fase 0: Fundação
"""

from .database import (
    test_engine,
    db_session,
    db_client,
    tenant_fixture,
    admin_user_fixture,
)

from .factories import (
    FontePagadoraFactory,
    BeneficiarioFactory,
    DependenteFactory,
    PensaoAlimenticiaFactory,
    InfoDepSauFactory,
    PlanoSaudeFactory,
    PrevidenciaComplementarFactory,
    RendimentoMensalFactory,
    ComprovanteRendimentosFactory,
)

__all__ = [
    # Database fixtures
    "test_engine",
    "db_session",
    "db_client",
    "tenant_fixture",
    "admin_user_fixture",
    
    # Factories
    "FontePagadoraFactory",
    "BeneficiarioFactory",
    "DependenteFactory",
    "PensaoAlimenticiaFactory",
    "InfoDepSauFactory",
    "PlanoSaudeFactory",
    "PrevidenciaComplementarFactory",
    "RendimentoMensalFactory",
    "ComprovanteRendimentosFactory",
]
