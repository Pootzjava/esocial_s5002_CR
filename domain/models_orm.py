"""
ORM Models for Database
Fase 0: Fundação

Modelos SQLAlchemy para persistência no banco de dados.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    ForeignKey,
    Numeric,
    Text,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from infrastructure.database import Base


class Tenant(Base):
    """Tenant/Cliente do sistema SaaS"""
    __tablename__ = "tenants"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    cnpj = Column(String(14), unique=True, nullable=False, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    ativo = Column(Boolean, default=True)
    plano = Column(String(50), default="free")  # free, starter, professional, enterprise, corporate
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    usuarios = relationship("Usuario", back_populates="tenant")
    comprovantes = relationship("ComprovanteRendimentos", back_populates="tenant")
    
    def __repr__(self):
        return f"<Tenant(id={self.id}, nome='{self.nome}', cnpj='{self.cnpj}')>"


class Usuario(Base):
    """Usuário do sistema"""
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    senha_hash = Column(String(255), nullable=False)
    nome = Column(String(255), nullable=False)
    ativo = Column(Boolean, default=True)
    eh_admin = Column(Boolean, default=False)
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255), nullable=True)
    ultimo_acesso = Column(DateTime, nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    tenant = relationship("Tenant", back_populates="usuarios")
    
    __table_args__ = (
        Index("idx_usuario_tenant_email", "tenant_id", "email"),
    )
    
    def __repr__(self):
        return f"<Usuario(id={self.id}, email='{self.email}')>"


class FontePagadora(Base):
    """Fonte pagadora (empresa)"""
    __tablename__ = "fontes_pagadoras"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    cnpj = Column(String(14), nullable=False, index=True)
    nome = Column(String(255), nullable=False)
    id_esocial = Column(String(50), nullable=True)
    ambiente = Column(String(20), default="PRODUCAO")  # PRODUCAO ou PRE_PRODUCACAO
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    tenant = relationship("Tenant")
    comprovantes = relationship("ComprovanteRendimentos", back_populates="fonte_pagadora")
    
    __table_args__ = (
        Index("idx_fonte_tenant_cnpj", "tenant_id", "cnpj"),
    )
    
    def __repr__(self):
        return f"<FontePagadora(id={self.id}, cnpj='{self.cnpj}')>"


class ComprovanteRendimentos(Base):
    """Comprovante de rendimentos"""
    __tablename__ = "comprovantes_rendimentos"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    fonte_pagadora_id = Column(Integer, ForeignKey("fontes_pagadoras.id"), nullable=True)
    
    # Dados do beneficiário
    cpf_beneficiario = Column(String(11), nullable=False, index=True)
    nome_beneficiario = Column(String(255), nullable=False)
    dt_nascimento = Column(String(10), nullable=True)
    
    # Status do processamento
    processado = Column(Boolean, default=False)
    arquivo_xml_origem = Column(String(500), nullable=True)
    arquivo_pdf_gerado = Column(String(500), nullable=True)
    erros_processamento = Column(Text, nullable=True)
    
    # Metadados
    ano_exercicio = Column(Integer, nullable=False, index=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processado_em = Column(DateTime, nullable=True)
    
    # Relacionamentos
    tenant = relationship("Tenant", back_populates="comprovantes")
    fonte_pagadora = relationship("FontePagadora", back_populates="comprovantes")
    dependentes = relationship("Dependente", back_populates="comprovante", cascade="all, delete-orphan")
    pensoes = relationship("PensaoAlimenticia", back_populates="comprovante", cascade="all, delete-orphan")
    planos_saude = relationship("PlanoSaude", back_populates="comprovante", cascade="all, delete-orphan")
    prev_complementar = relationship("PrevidenciaComplementar", back_populates="comprovante", cascade="all, delete-orphan")
    rendimentos_mensais = relationship("RendimentoMensal", back_populates="comprovante", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_comprovante_tenant_cpf", "tenant_id", "cpf_beneficiario"),
        Index("idx_comprovante_ano", "ano_exercicio"),
    )
    
    def __repr__(self):
        return f"<ComprovanteRendimentos(id={self.id}, cpf='{self.cpf_beneficiario}', ano={self.ano_exercicio})>"


class Dependente(Base):
    """Dependentes do beneficiário"""
    __tablename__ = "dependentes"
    
    id = Column(Integer, primary_key=True, index=True)
    comprovante_id = Column(Integer, ForeignKey("comprovantes_rendimentos.id"), nullable=False)
    cpf = Column(String(11), nullable=False)
    nome = Column(String(255), nullable=False)
    dt_nascimento = Column(String(10), nullable=False)
    tipo_dependente = Column(String(2), nullable=False)  # tp_dep do eSocial
    descricao_dependente = Column(String(255), nullable=True)  # descr_dep do eSocial
    
    # Relacionamentos
    comprovante = relationship("ComprovanteRendimentos", back_populates="dependentes")
    
    def __repr__(self):
        return f"<Dependente(id={self.id}, cpf='{self.cpf}', nome='{self.nome}')>"


class PensaoAlimenticia(Base):
    """Pensões alimentícias"""
    __tablename__ = "pensoes_alimenticias"
    
    id = Column(Integer, primary_key=True, index=True)
    comprovante_id = Column(Integer, ForeignKey("comprovantes_rendimentos.id"), nullable=False)
    cpf_beneficiario = Column(String(11), nullable=False)
    nome_beneficiario = Column(String(255), nullable=False)
    valor_mensal = Column(Numeric(15, 2), default=0.00)
    valor_13_salario = Column(Numeric(15, 2), default=0.00)
    valor_plr = Column(Numeric(15, 2), default=0.00)
    
    # Relacionamentos
    comprovante = relationship("ComprovanteRendimentos", back_populates="pensoes")
    
    def __repr__(self):
        return f"<PensaoAlimenticia(id={self.id}, cpf='{self.cpf_beneficiario}')>"


class PlanoSaude(Base):
    """Planos de saúde"""
    __tablename__ = "planos_saude"
    
    id = Column(Integer, primary_key=True, index=True)
    comprovante_id = Column(Integer, ForeignKey("comprovantes_rendimentos.id"), nullable=False)
    cnpj_operadora = Column(String(14), nullable=False)
    nome_operadora = Column(String(255), nullable=False)
    registro_ans = Column(String(20), nullable=False)
    valor_titular = Column(Numeric(15, 2), default=0.00)
    
    # Relacionamentos
    comprovante = relationship("ComprovanteRendimentos", back_populates="planos_saude")
    dependentes_plano = relationship("PlanoSaudeDependente", back_populates="plano_saude", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<PlanoSaude(id={self.id}, cnpj='{self.cnpj_operadora}')>"


class PlanoSaudeDependente(Base):
    """Dependentes de plano de saúde"""
    __tablename__ = "planos_saude_dependentes"
    
    id = Column(Integer, primary_key=True, index=True)
    plano_saude_id = Column(Integer, ForeignKey("planos_saude.id"), nullable=False)
    cpf_dep = Column(String(11), nullable=False)
    nm_dep = Column(String(255), nullable=False)
    dt_nasc_dep = Column(String(10), nullable=False)
    vlr_plano = Column(Numeric(15, 2), default=0.00)
    
    # Relacionamentos
    plano_saude = relationship("PlanoSaude", back_populates="dependentes_plano")
    
    def __repr__(self):
        return f"<PlanoSaudeDependente(id={self.id}, cpf='{self.cpf_dep}')>"


class PrevidenciaComplementar(Base):
    """Previdência complementar"""
    __tablename__ = "prev_complementar"
    
    id = Column(Integer, primary_key=True, index=True)
    comprovante_id = Column(Integer, ForeignKey("comprovantes_rendimentos.id"), nullable=False)
    cnpj_entidade = Column(String(14), nullable=False)
    nome_entidade = Column(String(255), nullable=False)
    tipo_previdencia = Column(String(1), nullable=False)  # 1=PGBL, 2=FAPI, 3=Funpresp, 4=Outros
    valor = Column(Numeric(15, 2), default=0.00)
    
    # Relacionamentos
    comprovante = relationship("ComprovanteRendimentos", back_populates="prev_complementar")
    
    def __repr__(self):
        return f"<PrevidenciaComplementar(id={self.id}, cnpj='{self.cnpj_entidade}')>"


class RendimentoMensal(Base):
    """Rendimentos mensais"""
    __tablename__ = "rendimentos_mensais"
    
    id = Column(Integer, primary_key=True, index=True)
    comprovante_id = Column(Integer, ForeignKey("comprovantes_rendimentos.id"), nullable=False)
    mes = Column(Integer, nullable=False)  # 1-12
    ano = Column(Integer, nullable=False)
    rendimento_tributavel = Column(Numeric(15, 2), default=0.00)
    contribuicao_prev = Column(Numeric(15, 2), default=0.00)
    imposto_retido = Column(Numeric(15, 2), default=0.00)
    rendimento_isento = Column(Numeric(15, 2), default=0.00)
    rendimento_exclusivo = Column(Numeric(15, 2), default=0.00)
    
    # Relacionamentos
    comprovante = relationship("ComprovanteRendimentos", back_populates="rendimentos_mensais")
    
    __table_args__ = (
        Index("idx_rendimento_comprovante_mes", "comprovante_id", "mes"),
    )
    
    def __repr__(self):
        return f"<RendimentoMensal(id={self.id}, mes={self.mes}, ano={self.ano})>"
