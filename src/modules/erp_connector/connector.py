"""
Conector de ERP - Fase 3: Enterprise Ready

Integração com sistemas ERP (Totvs, SAP, Senior) para importação de dados de funcionários e eventos.
"""
import csv
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path
from pydantic import BaseModel


class EmployeeData(BaseModel):
    """Dados de funcionário importados do ERP."""
    cpf: str
    nome: str
    matricula: str
    data_admissao: datetime
    cargo: Optional[str] = None
    salario: Optional[float] = None
    departamento: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True


class IncomeEventData(BaseModel):
    """Dados de evento de rendimentos importados do ERP."""
    cpf: str
    competencia: str  # Ano-mês (YYYY-MM)
    rendimento_bruto: float
    desconto_inss: float
    desconto_irrf: float
    outros_descontos: float = 0.0
    codigo_categoria: str = "101"
    
    class Config:
        arbitrary_types_allowed = True


class ERPConnector:
    """Conector base para integração com ERPs."""
    
    def __init__(self, erp_type: str = "generic"):
        self.erp_type = erp_type
    
    def connect(self, config: Dict[str, Any]) -> bool:
        """Estabelece conexão com o ERP."""
        raise NotImplementedError
    
    def fetch_employees(self, filters: Dict = None) -> List[EmployeeData]:
        """Busca lista de funcionários do ERP."""
        raise NotImplementedError
    
    def fetch_income_events(self, competencia: str, filters: Dict = None) -> List[IncomeEventData]:
        """Busca eventos de rendimentos do ERP."""
        raise NotImplementedError
    
    def test_connection(self) -> bool:
        """Testa conexão com o ERP."""
        raise NotImplementedError


class FileERPConnector(ERPConnector):
    """Conector via arquivos CSV/JSON (para ERPs sem API)."""
    
    def __init__(self, erp_type: str = "file"):
        super().__init__(erp_type)
        self.base_path: Optional[Path] = None
    
    def connect(self, config: Dict[str, Any]) -> bool:
        """Configura caminho base dos arquivos."""
        try:
            self.base_path = Path(config.get('base_path', '/tmp/erp_files'))
            return self.base_path.exists()
        except Exception:
            return False
    
    def fetch_employees_from_csv(self, file_name: str = 'funcionarios.csv') -> List[EmployeeData]:
        """Importa funcionários de arquivo CSV."""
        if not self.base_path:
            raise ValueError("ERP não conectado")
        
        file_path = self.base_path / file_name
        if not file_path.exists():
            return []
        
        employees = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    employee = EmployeeData(
                        cpf=row.get('cpf', ''),
                        nome=row.get('nome', ''),
                        matricula=row.get('matricula', ''),
                        data_admissao=datetime.strptime(row.get('data_admissao', '2024-01-01'), '%Y-%m-%d'),
                        cargo=row.get('cargo'),
                        salario=float(row.get('salario', 0)) if row.get('salario') else None,
                        departamento=row.get('departamento')
                    )
                    employees.append(employee)
                except Exception:
                    continue
        
        return employees
    
    def fetch_income_events_from_csv(self, file_name: str = 'rendimentos.csv') -> List[IncomeEventData]:
        """Importa eventos de rendimentos de arquivo CSV."""
        if not self.base_path:
            raise ValueError("ERP não conectado")
        
        file_path = self.base_path / file_name
        if not file_path.exists():
            return []
        
        events = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    event = IncomeEventData(
                        cpf=row.get('cpf', ''),
                        competencia=row.get('competencia', ''),
                        rendimento_bruto=float(row.get('rendimento_bruto', 0)),
                        desconto_inss=float(row.get('desconto_inss', 0)),
                        desconto_irrf=float(row.get('desconto_irrf', 0)),
                        outros_descontos=float(row.get('outros_descontos', 0)),
                        codigo_categoria=row.get('codigo_categoria', '101')
                    )
                    events.append(event)
                except Exception:
                    continue
        
        return events
    
    def fetch_employees_from_json(self, file_name: str = 'funcionarios.json') -> List[EmployeeData]:
        """Importa funcionários de arquivo JSON."""
        if not self.base_path:
            raise ValueError("ERP não conectado")
        
        file_path = self.base_path / file_name
        if not file_path.exists():
            return []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        employees = []
        for item in data:
            try:
                employee = EmployeeData(
                    cpf=item.get('cpf', ''),
                    nome=item.get('nome', ''),
                    matricula=item.get('matricula', ''),
                    data_admissao=datetime.strptime(item.get('data_admissao', '2024-01-01'), '%Y-%m-%d'),
                    cargo=item.get('cargo'),
                    salario=item.get('salario'),
                    departamento=item.get('departamento')
                )
                employees.append(employee)
            except Exception:
                continue
        
        return employees
    
    def test_connection(self) -> bool:
        """Testa se o caminho base existe."""
        return self.base_path is not None and self.base_path.exists()


class TotvsConnector(FileERPConnector):
    """Conector específico para Totvs Protheus/RM."""
    
    def __init__(self):
        super().__init__(erp_type="totvs")
    
    def fetch_employees(self, filters: Dict = None) -> List[EmployeeData]:
        """Importa funcionários do Totvs."""
        return self.fetch_employees_from_csv('totvs_funcionarios.csv')
    
    def fetch_income_events(self, competencia: str, filters: Dict = None) -> List[IncomeEventData]:
        """Importa rendimentos do Totvs."""
        file_name = f'totvs_rendimentos_{competencia}.csv'
        return self.fetch_income_events_from_csv(file_name)


class SAPConnector(FileERPConnector):
    """Conector específico para SAP RH."""
    
    def __init__(self):
        super().__init__(erp_type="sap")
    
    def fetch_employees(self, filters: Dict = None) -> List[EmployeeData]:
        """Importa funcionários do SAP."""
        return self.fetch_employees_from_json('sap_funcionarios.json')
    
    def fetch_income_events(self, competencia: str, filters: Dict = None) -> List[IncomeEventData]:
        """Importa rendimentos do SAP."""
        file_name = f'sap_rendimentos_{competencia}.json'
        return self.fetch_income_events_from_json(file_name)


class SeniorConnector(FileERPConnector):
    """Conector específico para Senior HCM."""
    
    def __init__(self):
        super().__init__(erp_type="senior")
    
    def fetch_employees(self, filters: Dict = None) -> List[EmployeeData]:
        """Importa funcionários do Senior."""
        return self.fetch_employees_from_csv('senior_funcionarios.csv')
    
    def fetch_income_events(self, competencia: str, filters: Dict = None) -> List[IncomeEventData]:
        """Importa rendimentos do Senior."""
        file_name = f'senior_rendimentos_{competencia}.csv'
        return self.fetch_income_events_from_csv(file_name)


def get_erp_connector(erp_type: str) -> ERPConnector:
    """Factory para criar conector baseado no tipo de ERP."""
    connectors = {
        'totvs': TotvsConnector,
        'sap': SAPConnector,
        'senior': SeniorConnector,
        'file': FileERPConnector,
        'generic': FileERPConnector
    }
    
    connector_class = connectors.get(erp_type.lower(), FileERPConnector)
    return connector_class()
