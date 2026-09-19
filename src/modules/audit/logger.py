"""
Módulo de Audit Logs - Fase 3: Enterprise Ready

Registra todas as ações dos usuários de forma imutável para compliance e segurança.
"""
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel


class ActionType(str, Enum):
    """Tipos de ações auditáveis."""
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    VIEW = "VIEW"
    EXPORT = "EXPORT"
    UPLOAD = "UPLOAD"
    APPROVE = "APPROVE"
    REJECT = "REJECT"


class AuditLog(BaseModel):
    """Modelo de log de auditoria."""
    id: Optional[int] = None
    tenant_id: int
    user_id: int
    user_email: str
    action: ActionType
    resource_type: str
    resource_id: Optional[int] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = None
    details: Optional[Dict[str, Any]] = None
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        data['timestamp'] = data.get('timestamp') or datetime.utcnow()
        super().__init__(**data)


class AuditLogger:
    """Logger de auditoria para registrar ações dos usuários."""
    
    def __init__(self, db_session=None):
        self.db_session = db_session
    
    def log(
        self,
        tenant_id: int,
        user_id: int,
        user_email: str,
        action: ActionType,
        resource_type: str,
        resource_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """
        Registra uma ação de auditoria.
        
        Args:
            tenant_id: ID do tenant
            user_id: ID do usuário
            user_email: Email do usuário
            action: Tipo de ação
            resource_type: Tipo de recurso (ex: 'employee', 'pdf_document')
            resource_id: ID do recurso afetado
            ip_address: IP do cliente
            user_agent: User agent do cliente
            details: Detalhes adicionais em JSON
            
        Returns:
            AuditLog criado
        """
        audit_log = AuditLog(
            tenant_id=tenant_id,
            user_id=user_id,
            user_email=user_email,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details
        )
        
        # Em produção, salvaria no banco de dados
        # self.db_session.add(audit_log)
        # self.db_session.commit()
        
        return audit_log
    
    def log_login(self, user_id: int, user_email: str, tenant_id: int, ip_address: str):
        """Registra login de usuário."""
        return self.log(
            tenant_id=tenant_id,
            user_id=user_id,
            user_email=user_email,
            action=ActionType.LOGIN,
            resource_type="user",
            resource_id=user_id,
            ip_address=ip_address
        )
    
    def log_logout(self, user_id: int, user_email: str, tenant_id: int):
        """Registra logout de usuário."""
        return self.log(
            tenant_id=tenant_id,
            user_id=user_id,
            user_email=user_email,
            action=ActionType.LOGOUT,
            resource_type="user",
            resource_id=user_id
        )
    
    def log_create(self, tenant_id: int, user_id: int, user_email: str, 
                   resource_type: str, resource_id: int, details: Dict = None):
        """Registra criação de recurso."""
        return self.log(
            tenant_id=tenant_id,
            user_id=user_id,
            user_email=user_email,
            action=ActionType.CREATE,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details
        )
    
    def log_update(self, tenant_id: int, user_id: int, user_email: str,
                   resource_type: str, resource_id: int, details: Dict = None):
        """Registra atualização de recurso."""
        return self.log(
            tenant_id=tenant_id,
            user_id=user_id,
            user_email=user_email,
            action=ActionType.UPDATE,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details
        )
    
    def log_delete(self, tenant_id: int, user_id: int, user_email: str,
                   resource_type: str, resource_id: int, details: Dict = None):
        """Registra exclusão de recurso."""
        return self.log(
            tenant_id=tenant_id,
            user_id=user_id,
            user_email=user_email,
            action=ActionType.DELETE,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details
        )
    
    def log_upload(self, tenant_id: int, user_id: int, user_email: str,
                   file_name: str, file_size: int, event_count: int):
        """Registra upload de arquivo XML."""
        return self.log(
            tenant_id=tenant_id,
            user_id=user_id,
            user_email=user_email,
            action=ActionType.UPLOAD,
            resource_type="xml_file",
            details={
                "file_name": file_name,
                "file_size": file_size,
                "event_count": event_count
            }
        )
    
    def log_export(self, tenant_id: int, user_id: int, user_email: str,
                   export_type: str, record_count: int):
        """Registra exportação de dados."""
        return self.log(
            tenant_id=tenant_id,
            user_id=user_id,
            user_email=user_email,
            action=ActionType.EXPORT,
            resource_type=export_type,
            details={"record_count": record_count}
        )
