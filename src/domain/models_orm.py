"""
Modelos ORM - SQLAlchemy
Fase 1: MVP Core
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from src.infrastructure.database import Base


class Tenant(Base):
    """Modelo de Tenant (Empresa/Cliente)"""
    __tablename__ = "tenants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    cnpj = Column(String(18), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20))
    is_active = Column(Boolean, default=True)
    plan = Column(String(50), default="free")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("User", back_populates="tenant")
    employees = relationship("Employee", back_populates="tenant")


class User(Base):
    """Modelo de Usuário"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    tenant = relationship("Tenant", back_populates="users")


class Employee(Base):
    """Modelo de Funcionário/Beneficiário"""
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    cpf = Column(String(14), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    nis_pis = Column(String(15))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    tenant = relationship("Tenant", back_populates="employees")
    income_events = relationship("IncomeEvent", back_populates="employee")


class IncomeEvent(Base):
    """Modelo de Evento de Rendimentos (S-5002)"""
    __tablename__ = "income_events"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    event_type = Column(String(20), nullable=False)  # S-5002
    reference_year = Column(Integer, nullable=False, index=True)
    reference_month = Column(Integer, nullable=False)
    gross_amount = Column(Float, nullable=False)
    net_amount = Column(Float, nullable=False)
    irrf_amount = Column(Float, default=0.0)
    inss_amount = Column(Float, default=0.0)
    xml_data = Column(JSON)  # Dados completos do XML
    processed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    employee = relationship("Employee", back_populates="income_events")


class PDFDocument(Base):
    """Modelo de Documento PDF Gerado"""
    __tablename__ = "pdf_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    document_type = Column(String(50), nullable=False)  # comprovante_rendimentos
    reference_year = Column(Integer, nullable=False, index=True)
    file_path = Column(String(500), nullable=False)
    file_hash = Column(String(64))  # SHA256 para integridade
    status = Column(String(20), default="generated")  # generated, sent, downloaded
    qr_code_data = Column(Text)  # Dados do QR Code
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant")
    employee = relationship("Employee")


class ProcessingJob(Base):
    """Modelo de Job de Processamento"""
    __tablename__ = "processing_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    job_type = Column(String(50), nullable=False)  # xml_upload, pdf_generation
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    total_items = Column(Integer, default=0)
    processed_items = Column(Integer, default=0)
    error_message = Column(Text)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    tenant = relationship("Tenant")
