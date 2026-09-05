"""
Integração com ERPs (Totvs, SAP, Oracle, Senior) para importação de dados de funcionários e eventos.
Conforme requisitos da Fase 3: Enterprise Ready.
Suporta arquivos TXT no formato padrão de importação de folha de pagamento.
"""
import csv
import io
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class EmployeeERPData:
    """Dados de funcionário vindos de ERP."""
    matricula: str
    nome: str
    cpf: str
    cargo: str
    departamento: str
    data_admissao: str
    salario_base: float
    categoria: str = "01"  # Código de categoria no eSocial


@dataclass
class IncomeEventERPData:
    """Dados de evento de rendimento vindo de ERP."""
    matricula: str
    tipo_evento: str  # S-5002, S-5003, etc.
    competencia: str  # Ano-mês (YYYY-MM)
    valor_bruto: float
    valor_liquido: float
    desconto_irrf: float
    desconto_inss: float
    outros_descontos: float = 0.0
    observacoes: str = ""


class ERPIntegrationService:
    """Serviço de integração com sistemas ERP."""

    @staticmethod
    def parse_totvs_txt(content: str) -> Dict[str, Any]:
        """
        Parse de arquivo TXT no formato Totvs.
        Formato esperado: CSV com delimitador pipe (|)
        """
        employees = []
        events = []
        
        lines = content.strip().split('\n')
        
        for line in lines:
            if not line.strip():
                continue
            
            parts = line.split('|')
            
            # Detectar tipo de registro pelo primeiro campo
            if len(parts) < 2:
                continue
            
            record_type = parts[0].strip()
            
            # Registro de funcionário (ex: FUNCIONARIO|matricula|nome|cpf|...)
            if record_type == "FUNCIONARIO" and len(parts) >= 9:
                employees.append(EmployeeERPData(
                    matricula=parts[1].strip(),
                    nome=parts[2].strip(),
                    cpf=parts[3].strip(),
                    cargo=parts[4].strip(),
                    departamento=parts[5].strip(),
                    data_admissao=parts[6].strip(),
                    salario_base=float(parts[7].replace(',', '.')),
                    categoria=parts[8].strip() if len(parts) > 8 else "01",
                ))
            
            # Registro de evento (ex: EVENTO|matricula|tipo|competencia|bruto|liquido|irrf|inss)
            elif record_type == "EVENTO" and len(parts) >= 8:
                events.append(IncomeEventERPData(
                    matricula=parts[1].strip(),
                    tipo_evento=parts[2].strip(),
                    competencia=parts[3].strip(),
                    valor_bruto=float(parts[4].replace(',', '.')),
                    valor_liquido=float(parts[5].replace(',', '.')),
                    desconto_irrf=float(parts[6].replace(',', '.')),
                    desconto_inss=float(parts[7].replace(',', '.')),
                    outros_descontos=float(parts[8].replace(',', '.')) if len(parts) > 8 else 0.0,
                ))
        
        return {
            "employees": employees,
            "events": events,
            "source": "TOTVS",
            "processed_at": datetime.utcnow().isoformat(),
        }

    @staticmethod
    def parse_sap_csv(content: str) -> Dict[str, Any]:
        """
        Parse de arquivo CSV no formato SAP.
        Formato esperado: CSV padrão com cabeçalho
        """
        employees = []
        events = []
        
        # Usar StringIO para tratar string como arquivo
        csv_file = io.StringIO(content)
        reader = csv.DictReader(csv_file, delimiter=';')
        
        for row in reader:
            # Detectar tipo de registro
            record_type = row.get('TIPO_REGISTRO', '').strip()
            
            if record_type == 'FUNC':
                employees.append(EmployeeERPData(
                    matricula=row.get('MATRICULA', '').strip(),
                    nome=row.get('NOME', '').strip(),
                    cpf=row.get('CPF', '').strip(),
                    cargo=row.get('CARGO', '').strip(),
                    departamento=row.get('DEPARTAMENTO', '').strip(),
                    data_admissao=row.get('DATA_ADMISSAO', '').strip(),
                    salario_base=float(row.get('SALARIO', '0').replace(',', '.')),
                    categoria=row.get('CATEGORIA', '01').strip(),
                ))
            elif record_type == 'EVT':
                events.append(IncomeEventERPData(
                    matricula=row.get('MATRICULA', '').strip(),
                    tipo_evento=row.get('TIPO_EVENTO', '').strip(),
                    competencia=row.get('COMPETENCIA', '').strip(),
                    valor_bruto=float(row.get('VALOR_BRUTO', '0').replace(',', '.')),
                    valor_liquido=float(row.get('VALOR_LIQUIDO', '0').replace(',', '.')),
                    desconto_irrf=float(row.get('DESCONTO_IRRF', '0').replace(',', '.')),
                    desconto_inss=float(row.get('DESCONTO_INSS', '0').replace(',', '.')),
                ))
        
        return {
            "employees": employees,
            "events": events,
            "source": "SAP",
            "processed_at": datetime.utcnow().isoformat(),
        }

    @staticmethod
    def parse_oracle_xml(content: str) -> Dict[str, Any]:
        """
        Parse de arquivo XML no formato Oracle HCM.
        Implementação simplificada - em produção usaria xml.etree.ElementTree ou lxml
        """
        # Em produção, implementar parser XML real
        # Esta é uma implementação placeholder
        employees = []
        events = []
        
        # Placeholder para demonstração
        # Na implementação real, faria parse do XML Oracle HCM
        
        return {
            "employees": employees,
            "events": events,
            "source": "ORACLE",
            "processed_at": datetime.utcnow().isoformat(),
            "warning": "Parser Oracle XML em desenvolvimento",
        }

    @staticmethod
    def parse_senior_txt(content: str) -> Dict[str, Any]:
        """
        Parse de arquivo TXT no formato Senior Sistemas.
        Similar ao Totvs mas com layout específico
        """
        # Implementação similar ao Totvs com ajustes de layout
        return ERPIntegrationService.parse_totvs_txt(content)

    @staticmethod
    def detect_format(content: str) -> str:
        """
        Detecta automaticamente o formato do arquivo ERP.
        Retorna: 'TOTVS', 'SAP', 'ORACLE', 'SENIOR' ou 'UNKNOWN'
        """
        lines = content.strip().split('\n')
        
        # Verificar se é CSV com cabeçalho
        if ';' in lines[0] and 'TIPO_REGISTRO' in lines[0]:
            return 'SAP'
        
        # Verificar se é XML
        if content.strip().startswith('<?xml') or content.strip().startswith('<'):
            return 'ORACLE'
        
        # Verificar padrões específicos
        first_line = lines[0] if lines else ''
        
        if first_line.startswith('FUNCIONARIO|') or first_line.startswith('EVENTO|'):
            return 'TOTVS'
        
        if 'SENIOR' in first_line.upper():
            return 'SENIOR'
        
        return 'UNKNOWN'

    @staticmethod
    def parse_auto(content: str) -> Dict[str, Any]:
        """
        Detecta automaticamente o formato e faz o parse.
        """
        format_type = ERPIntegrationService.detect_format(content)
        
        parsers = {
            'TOTVS': ERPIntegrationService.parse_totvs_txt,
            'SAP': ERPIntegrationService.parse_sap_csv,
            'ORACLE': ERPIntegrationService.parse_oracle_xml,
            'SENIOR': ERPIntegrationService.parse_senior_txt,
        }
        
        parser_func = parsers.get(format_type)
        
        if not parser_func:
            raise ValueError(f"Formato de arquivo não reconhecido: {format_type}")
        
        result = parser_func(content)
        result['detected_format'] = format_type
        
        return result
