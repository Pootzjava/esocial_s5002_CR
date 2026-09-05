"""
eSocial Rendimentos SaaS - Core Domain Models
Fase 0: Fundação

Módulo contendo os modelos de domínio principais do sistema.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from dataclasses import dataclass, field
from enum import Enum


class AmbienteType(str, Enum):
    """Tipo de ambiente eSocial"""
    PRODUCAO = "PRODUCAO"
    PRE_PRODUCACAO = "PRE_PRODUCACAO"


class SituacaoPessoa(str, Enum):
    """Situação da pessoa física"""
    ATIVA = "ATIVA"
    SUSPENSA = "SUSPENSA"
    CANCELADA = "CANCELADA"


@dataclass
class FontePagadora:
    """Dados da fonte pagadora (empresa)"""
    cnpj: str
    nome: str
    id_esocial: Optional[str] = None
    ambiente: AmbienteType = AmbienteType.PRODUCAO
    
    def validar_cnpj(self) -> bool:
        """Valida o formato do CNPJ"""
        if len(self.cnpj) != 14:
            return False
        return self.cnpj.isdigit()


@dataclass
class Beneficiario:
    """Dados do beneficiário (pessoa física)"""
    cpf: str
    nome: str
    dt_nascimento: Optional[str] = None
    situacao: SituacaoPessoa = SituacaoPessoa.ATIVA
    
    def validar_cpf(self) -> bool:
        """Valida o formato do CPF"""
        if len(self.cpf) != 11:
            return False
        return self.cpf.isdigit()


@dataclass
class Dependente:
    """Dados de um dependente"""
    cpf: str
    nome: str
    dt_nascimento: str
    tipo_dependente: str  # tp_dep do eSocial
    descricao_dependente: str  # descr_dep do eSocial


@dataclass
class PensaoAlimenticia:
    """Dados de pensão alimentícia"""
    cpf_beneficiario: str
    nome_beneficiario: str
    valor_mensal: Decimal = Decimal('0.00')
    valor_13_salario: Decimal = Decimal('0.00')
    valor_plr: Decimal = Decimal('0.00')


@dataclass
class InfoDepSau:
    """Dependente de plano de saúde"""
    cpf_dep: str
    nm_dep: str
    dt_nasc_dep: str
    vlr_plano: Decimal = Decimal('0.00')


@dataclass
class PlanoSaude:
    """Dados de plano de saúde"""
    cnpj_operadora: str
    nome_operadora: str
    registro_ans: str
    valor_titular: Decimal = Decimal('0.00')
    dependentes: List[InfoDepSau] = field(default_factory=list)


@dataclass
class PrevidenciaComplementar:
    """Dados de previdência complementar"""
    cnpj_entidade: str
    nome_entidade: str
    tipo_previdencia: str  # 1=PGBL, 2=FAPI, 3=Funpresp, 4=Outros
    valor: Decimal = Decimal('0.00')


@dataclass
class RendimentoMensal:
    """Rendimentos de um mês específico"""
    mes: int
    ano: int
    rendimento_tributavel: Decimal = Decimal('0.00')
    contribuicao_prev: Decimal = Decimal('0.00')
    imposto_retido: Decimal = Decimal('0.00')
    rendimento_isento: Decimal = Decimal('0.00')
    rendimento_exclusivo: Decimal = Decimal('0.00')


@dataclass
class ComprovanteRendimentos:
    """Comprovante de rendimentos completo"""
    id: Optional[int] = None
    tenant_id: str = "default"
    
    # Fonte pagadora
    fonte_pagadora: Optional[FontePagadora] = None
    
    # Beneficiário
    beneficiario: Optional[Beneficiario] = None
    
    # Dependentes
    dependentes: List[Dependente] = field(default_factory=list)
    
    # Pensões
    pensoes_alimenticias: List[PensaoAlimenticia] = field(default_factory=list)
    
    # Planos de saúde
    planos_saude: List[PlanoSaude] = field(default_factory=list)
    
    # Previdência complementar
    prev_complementar: List[PrevidenciaComplementar] = field(default_factory=list)
    
    # Rendimentos mensais
    rendimentos_mensais: List[RendimentoMensal] = field(default_factory=list)
    
    # 13º salário
    rendimento_13_salario: Optional[RendimentoMensal] = None
    
    # PLR/Participação nos Lucros
    rendimento_plr: Optional[RendimentoMensal] = None
    
    # Metadados
    criado_em: datetime = field(default_factory=datetime.utcnow)
    atualizado_em: datetime = field(default_factory=datetime.utcnow)
    processado: bool = False
    arquivo_xml_origem: Optional[str] = None
    arquivo_pdf_gerado: Optional[str] = None
    
    def total_rendimentos_tributaveis(self) -> Decimal:
        """Calcula o total de rendimentos tributáveis anuais"""
        total = sum(r.rendimento_tributavel for r in self.rendimentos_mensais)
        if self.rendimento_13_salario:
            total += self.rendimento_13_salario.rendimento_tributavel
        if self.rendimento_plr:
            total += self.rendimento_plr.rendimento_tributavel
        return total
    
    def total_imposto_retido(self) -> Decimal:
        """Calcula o total de imposto retido anual"""
        total = sum(r.imposto_retido for r in self.rendimentos_mensais)
        if self.rendimento_13_salario:
            total += self.rendimento_13_salario.imposto_retido
        if self.rendimento_plr:
            total += self.rendimento_plr.imposto_retido
        return total
