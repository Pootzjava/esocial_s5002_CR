"""
Testes de integração para Integração ERP (Fase 3: Enterprise Ready).
Testa upload e parse de arquivos de Totvs, SAP, Oracle e Senior.
"""
import pytest
from fastapi.testclient import TestClient
from io import BytesIO
from src.api.main import app
from src.infrastructure.database import get_db, engine
from src.domain.models_orm import Tenant, User, UserRole
from sqlalchemy.orm import sessionmaker

client = TestClient(app)

# Configurar banco de dados de teste
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Cria sessão de banco de dados para testes."""
    from src.domain.models_orm import Base
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
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
    # OAuth2PasswordRequestForm espera form-data, não JSON
    response = client.post("/api/v1/auth/login", data={
        "username": test_user.username,
        "password": "password123"
    })
    assert response.status_code == 200
    return response.json()["access_token"]


class TestERPIntegrationEndpoints:
    """Testes para endpoints de Integração ERP."""

    def test_get_supported_formats(self, auth_token):
        """Testa listagem de formatos suportados."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = client.get("/api/v1/erp/supported-formats", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "formats" in data
        assert len(data["formats"]) >= 4  # Totvs, SAP, Oracle, Senior
        
        # Verificar Totvs
        totvs_format = next(f for f in data["formats"] if f["name"] == "TOTVS")
        assert totvs_format["delimiter"] == "|"
        assert "FUNCIONARIO" in totvs_format["record_types"]
        
        # Verificar SAP
        sap_format = next(f for f in data["formats"] if f["name"] == "SAP")
        assert sap_format["delimiter"] == ";"
        assert sap_format["has_header"] is True
        
        assert data["auto_detect"] is True

    def test_import_totvs_file_success(self, auth_token):
        """Testa importação de arquivo Totvs com sucesso."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Criar arquivo Totvs de exemplo
        totvs_content = """FUNCIONARIO|001|João Silva|123.456.789-00|Analista|TI|2020-01-15|5000.00|01
FUNCIONARIO|002|Maria Santos|987.654.321-00|Gerente|RH|2019-03-20|8000.00|01
EVENTO|001|S-5002|2024-01|5000.00|4500.00|500.00|450.00|0.00
EVENTO|002|S-5002|2024-01|8000.00|7200.00|800.00|720.00|0.00
"""
        
        files = {"file": ("totvs.txt", BytesIO(totvs_content.encode('utf-8')), "text/plain")}
        data = {"dry_run": True}
        
        response = client.post("/api/v1/erp/import", headers=headers, files=files, data=data)
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert result["data"]["detected_format"] == "TOTVS"
        assert result["data"]["source"] == "TOTVS"
        assert result["data"]["employees_count"] == 2
        assert result["data"]["events_count"] == 2
        assert result["dry_run"] is True
        
        # Verificar preview
        assert len(result["data"]["employees_preview"]) <= 5

    def test_import_sap_file_success(self, auth_token):
        """Testa importação de arquivo SAP com sucesso."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Criar arquivo SAP de exemplo
        sap_content = """TIPO_REGISTRO;MATRICULA;NOME;CPF;CARGO;DEPARTAMENTO;DATA_ADMISSAO;SALARIO;CATEGORIA
FUNC;003;Pedro Almeida;111.222.333-44;Desenvolvedor;Engenharia;2021-06-10;6000.00;01
EVT;003;S-5002;2024-01;6000.00;5400.00;600.00;540.00
"""
        
        files = {"file": ("sap.csv", BytesIO(sap_content.encode('utf-8')), "text/csv")}
        data = {"dry_run": False}
        
        response = client.post("/api/v1/erp/import", headers=headers, files=files, data=data)
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert result["data"]["detected_format"] == "SAP"
        assert result["data"]["source"] == "SAP"
        assert result["data"]["employees_count"] == 1
        assert result["data"]["events_count"] == 1

    def test_import_unknown_format_error(self, auth_token):
        """Testa erro ao importar formato desconhecido."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Conteúdo em formato não reconhecível
        unknown_content = """DADOS ALEATÓRIOS QUE NÃO SE ENCAIXAM EM NENHUM FORMATO
LINHA 2 SEM ESTRUTURA DEFINIDA
"""
        
        files = {"file": ("unknown.txt", BytesIO(unknown_content.encode('utf-8')), "text/plain")}
        
        response = client.post("/api/v1/erp/import", headers=headers, files=files)
        
        # Deve retornar erro 400 pois o formato não foi reconhecido
        assert response.status_code == 400
        assert "Formato de arquivo não reconhecido" in response.json()["detail"] or \
               "Erro ao processar arquivo" in response.json()["detail"]

    def test_import_empty_file_error(self, auth_token):
        """Testa erro ao importar arquivo vazio."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        files = {"file": ("empty.txt", BytesIO(b""), "text/plain")}
        
        response = client.post("/api/v1/erp/import", headers=headers, files=files)
        
        # Arquivo vazio pode causar erro ou retornar 0 registros
        assert response.status_code in [200, 400]

    def test_import_unauthorized(self):
        """Testa acesso sem autenticação."""
        files = {"file": ("test.txt", BytesIO(b"teste"), "text/plain")}
        
        response = client.post("/api/v1/erp/import", files=files)
        
        assert response.status_code in [401, 403]


class TestERPParserService:
    """Testes unitários para ERPIntegrationService."""

    def test_parse_totvs_txt(self):
        """Testa parser de arquivo Totvs."""
        from src.integrations.erp.parser import ERPIntegrationService
        
        content = """FUNCIONARIO|001|João Silva|123.456.789-00|Analista|TI|2020-01-15|5000.00|01
EVENTO|001|S-5002|2024-01|5000.00|4500.00|500.00|450.00
"""
        
        result = ERPIntegrationService.parse_totvs_txt(content)
        
        assert result["source"] == "TOTVS"
        assert len(result["employees"]) == 1
        assert len(result["events"]) == 1
        
        employee = result["employees"][0]
        assert employee.matricula == "001"
        assert employee.nome == "João Silva"
        assert employee.cpf == "123.456.789-00"
        assert employee.salario_base == 5000.00

    def test_parse_sap_csv(self):
        """Testa parser de arquivo SAP."""
        from src.integrations.erp.parser import ERPIntegrationService
        
        content = """TIPO_REGISTRO;MATRICULA;NOME;CPF;CARGO;DEPARTAMENTO;DATA_ADMISSAO;SALARIO;CATEGORIA
FUNC;002;Maria Santos;987.654.321-00;Gerente;RH;2019-03-20;8000.00;01
EVT;002;S-5002;2024-01;8000.00;7200.00;800.00;720.00
"""
        
        result = ERPIntegrationService.parse_sap_csv(content)
        
        assert result["source"] == "SAP"
        assert len(result["employees"]) == 1
        assert len(result["events"]) == 1
        
        employee = result["employees"][0]
        assert employee.matricula == "002"
        assert employee.nome == "Maria Santos"

    def test_detect_format_totvs(self):
        """Testa detecção automática de formato Totvs."""
        from src.integrations.erp.parser import ERPIntegrationService
        
        content = "FUNCIONARIO|001|Nome|CPF..."
        format_type = ERPIntegrationService.detect_format(content)
        
        assert format_type == "TOTVS"

    def test_detect_format_sap(self):
        """Testa detecção automática de formato SAP."""
        from src.integrations.erp.parser import ERPIntegrationService
        
        content = "TIPO_REGISTRO;MATRICULA;NOME..."
        format_type = ERPIntegrationService.detect_format(content)
        
        assert format_type == "SAP"

    def test_detect_format_oracle_xml(self):
        """Testa detecção automática de formato Oracle XML."""
        from src.integrations.erp.parser import ERPIntegrationService
        
        content = "<?xml version='1.0'?><ROOT>...</ROOT>"
        format_type = ERPIntegrationService.detect_format(content)
        
        assert format_type == "ORACLE"

    def test_parse_auto(self):
        """Testa parser automático que detecta formato."""
        from src.integrations.erp.parser import ERPIntegrationService
        
        totvs_content = "FUNCIONARIO|001|Nome|123.456.789-00|Cargo|Dept|2020-01-01|1000.00|01"
        
        result = ERPIntegrationService.parse_auto(totvs_content)
        
        assert result["detected_format"] == "TOTVS"
        assert result["source"] == "TOTVS"
        assert len(result["employees"]) == 1
