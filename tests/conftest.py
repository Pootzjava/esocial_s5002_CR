"""
Pytest Configuration
Fase 0: Fundação

Configuração base para testes automatizados.
"""

import sys
from pathlib import Path

# Adicionar o diretório raiz ao path para imports
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Configurações do pytest
pytest_plugins = []


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
