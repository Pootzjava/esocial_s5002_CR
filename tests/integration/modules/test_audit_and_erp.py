"""
Testes do Módulo de Audit Logs - Fase 3: Enterprise Ready
"""
import pytest
from datetime import datetime
from src.modules.audit.logger import AuditLogger, AuditLog, ActionType


class TestAuditLogger:
    """Testes para o logger de auditoria."""
    
    def test_create_audit_log(self):
        """Testa criação básica de log de auditoria."""
        log = AuditLog(
            tenant_id=1,
            user_id=100,
            user_email="user@example.com",
            action=ActionType.LOGIN,
            resource_type="user"
        )
        
        assert log.tenant_id == 1
        assert log.user_id == 100
        assert log.user_email == "user@example.com"
        assert log.action == ActionType.LOGIN
        assert log.resource_type == "user"
        assert log.timestamp is not None
    
    def test_audit_log_with_details(self):
        """Testa log com detalhes adicionais."""
        log = AuditLog(
            tenant_id=1,
            user_id=100,
            user_email="user@example.com",
            action=ActionType.CREATE,
            resource_type="employee",
            resource_id=50,
            details={"name": "João Silva", "cpf": "123.456.789-00"}
        )
        
        assert log.details["name"] == "João Silva"
        assert log.details["cpf"] == "123.456.789-00"
    
    def test_action_types_enum(self):
        """Testa todos os tipos de ação."""
        actions = [
            ActionType.LOGIN,
            ActionType.LOGOUT,
            ActionType.CREATE,
            ActionType.UPDATE,
            ActionType.DELETE,
            ActionType.VIEW,
            ActionType.EXPORT,
            ActionType.UPLOAD,
            ActionType.APPROVE,
            ActionType.REJECT
        ]
        
        assert len(actions) == 10
        assert ActionType.LOGIN.value == "LOGIN"
        assert ActionType.CREATE.value == "CREATE"
    
    def test_audit_logger_login(self):
        """Testa registro de login."""
        logger = AuditLogger()
        log = logger.log_login(
            user_id=100,
            user_email="user@example.com",
            tenant_id=1,
            ip_address="192.168.1.100"
        )
        
        assert log.action == ActionType.LOGIN
        assert log.resource_type == "user"
        assert log.ip_address == "192.168.1.100"
    
    def test_audit_logger_logout(self):
        """Testa registro de logout."""
        logger = AuditLogger()
        log = logger.log_logout(
            user_id=100,
            user_email="user@example.com",
            tenant_id=1
        )
        
        assert log.action == ActionType.LOGOUT
        assert log.resource_type == "user"
    
    def test_audit_logger_create(self):
        """Testa registro de criação de recurso."""
        logger = AuditLogger()
        log = logger.log_create(
            tenant_id=1,
            user_id=100,
            user_email="user@example.com",
            resource_type="employee",
            resource_id=50,
            details={"name": "João"}
        )
        
        assert log.action == ActionType.CREATE
        assert log.resource_type == "employee"
        assert log.resource_id == 50
    
    def test_audit_logger_update(self):
        """Testa registro de atualização de recurso."""
        logger = AuditLogger()
        log = logger.log_update(
            tenant_id=1,
            user_id=100,
            user_email="user@example.com",
            resource_type="employee",
            resource_id=50,
            details={"field": "salary", "old_value": 5000, "new_value": 6000}
        )
        
        assert log.action == ActionType.UPDATE
        assert log.details["field"] == "salary"
    
    def test_audit_logger_delete(self):
        """Testa registro de exclusão de recurso."""
        logger = AuditLogger()
        log = logger.log_delete(
            tenant_id=1,
            user_id=100,
            user_email="user@example.com",
            resource_type="employee",
            resource_id=50
        )
        
        assert log.action == ActionType.DELETE
        assert log.resource_id == 50
    
    def test_audit_logger_upload(self):
        """Testa registro de upload de arquivo."""
        logger = AuditLogger()
        log = logger.log_upload(
            tenant_id=1,
            user_id=100,
            user_email="user@example.com",
            file_name="esocial.xml",
            file_size=1024,
            event_count=50
        )
        
        assert log.action == ActionType.UPLOAD
        assert log.resource_type == "xml_file"
        assert log.details["file_name"] == "esocial.xml"
        assert log.details["event_count"] == 50
    
    def test_audit_logger_export(self):
        """Testa registro de exportação de dados."""
        logger = AuditLogger()
        log = logger.log_export(
            tenant_id=1,
            user_id=100,
            user_email="user@example.com",
            export_type="pdf_batch",
            record_count=100
        )
        
        assert log.action == ActionType.EXPORT
        assert log.resource_type == "pdf_batch"
        assert log.details["record_count"] == 100


class TestERPConnector:
    """Testes para conectores de ERP."""
    
    def test_get_erp_connector_totvs(self):
        """Testa factory para conector Totvs."""
        from src.modules.erp_connector import get_erp_connector, TotvsConnector
        
        connector = get_erp_connector("totvs")
        assert isinstance(connector, TotvsConnector)
        assert connector.erp_type == "totvs"
    
    def test_get_erp_connector_sap(self):
        """Testa factory para conector SAP."""
        from src.modules.erp_connector import get_erp_connector, SAPConnector
        
        connector = get_erp_connector("sap")
        assert isinstance(connector, SAPConnector)
        assert connector.erp_type == "sap"
    
    def test_get_erp_connector_senior(self):
        """Testa factory para conector Senior."""
        from src.modules.erp_connector import get_erp_connector, SeniorConnector
        
        connector = get_erp_connector("senior")
        assert isinstance(connector, SeniorConnector)
        assert connector.erp_type == "senior"
    
    def test_get_erp_connector_generic(self):
        """Testa factory para conector genérico."""
        from src.modules.erp_connector import get_erp_connector, FileERPConnector
        
        connector = get_erp_connector("generic")
        assert isinstance(connector, FileERPConnector)
    
    def test_employee_data_model(self):
        """Testa modelo de dados de funcionário."""
        from src.modules.erp_connector import EmployeeData
        
        employee = EmployeeData(
            cpf="123.456.789-00",
            nome="João Silva",
            matricula="001",
            data_admissao=datetime(2024, 1, 15),
            cargo="Analista",
            salario=5000.00,
            departamento="TI"
        )
        
        assert employee.cpf == "123.456.789-00"
        assert employee.nome == "João Silva"
        assert employee.salario == 5000.00
    
    def test_income_event_data_model(self):
        """Testa modelo de dados de evento de rendimentos."""
        from src.modules.erp_connector import IncomeEventData
        
        event = IncomeEventData(
            cpf="123.456.789-00",
            competencia="2024-01",
            rendimento_bruto=5000.00,
            desconto_inss=450.00,
            desconto_irrf=350.00,
            outros_descontos=100.00
        )
        
        assert event.competencia == "2024-01"
        assert event.rendimento_bruto == 5000.00
        assert event.desconto_irrf == 350.00
    
    def test_file_connector_connection(self):
        """Testa conexão do conector de arquivos."""
        from src.modules.erp_connector import FileERPConnector
        import tempfile
        import os
        
        connector = FileERPConnector()
        
        # Cria diretório temporário para teste
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {"base_path": tmpdir}
            result = connector.connect(config)
            
            assert result is True
            assert connector.test_connection() is True
    
    def test_file_connector_no_connection(self):
        """Testa falha de conexão com caminho inválido."""
        from src.modules.erp_connector import FileERPConnector
        
        connector = FileERPConnector()
        config = {"base_path": "/caminho/invalido/que/nao/existe"}
        result = connector.connect(config)
        
        assert result is False
