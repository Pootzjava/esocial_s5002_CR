"""
Serviço de Audit Log para rastreamento imutável de todas as ações dos usuários.
Conforme requisitos da Fase 3: Enterprise Ready.
"""
from datetime import datetime
from typing import Optional, Any, Dict
from sqlalchemy.orm import Session
from src.domain.models_orm import AuditLog


class AuditLogService:
    """Serviço para criação e consulta de logs de auditoria."""

    @staticmethod
    def log_action(
        db: Session,
        user_id: int,
        tenant_id: int,
        action: str,
        resource_type: str,
        resource_id: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        """
        Registra uma ação de auditoria de forma imutável.
        
        Args:
            db: Sessão do banco de dados
            user_id: ID do usuário que realizou a ação
            tenant_id: ID do tenant
            action: Tipo de ação (CREATE, UPDATE, DELETE, VIEW, EXPORT, LOGIN, LOGOUT)
            resource_type: Tipo de recurso (User, Employee, PDFDocument, etc.)
            resource_id: ID do recurso afetado
            details: Detalhes adicionais em JSON
            ip_address: IP do cliente
            user_agent: User agent do cliente
            
        Returns:
            AuditLog criado
        """
        audit_log = AuditLog(
            user_id=user_id,
            tenant_id=tenant_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            new_value=details or {},
            ip_address=ip_address,
            user_agent=user_agent,
            created_at=datetime.utcnow(),
        )
        
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        
        return audit_log

    @staticmethod
    def get_logs_by_tenant(
        db: Session,
        tenant_id: int,
        limit: int = 100,
        offset: int = 0,
        action_filter: Optional[str] = None,
        resource_type_filter: Optional[str] = None,
        user_id_filter: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> list[AuditLog]:
        """
        Recupera logs de auditoria de um tenant com filtros opcionais.
        
        Args:
            db: Sessão do banco de dados
            tenant_id: ID do tenant
            limit: Limite de registros
            offset: Offset para paginação
            action_filter: Filtrar por tipo de ação
            resource_type_filter: Filtrar por tipo de recurso
            user_id_filter: Filtrar por usuário
            start_date: Data inicial
            end_date: Data final
            
        Returns:
            Lista de AuditLog
        """
        query = db.query(AuditLog).filter(AuditLog.tenant_id == tenant_id)
        
        if action_filter:
            query = query.filter(AuditLog.action == action_filter)
        
        if resource_type_filter:
            query = query.filter(AuditLog.resource_type == resource_type_filter)
        
        if user_id_filter:
            query = query.filter(AuditLog.user_id == user_id_filter)
        
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)
        
        return query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()

    @staticmethod
    def export_logs_to_csv(
        db: Session,
        tenant_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> str:
        """
        Exporta logs de auditoria para formato CSV.
        
        Args:
            db: Sessão do banco de dados
            tenant_id: ID do tenant
            start_date: Data inicial
            end_date: Data final
            
        Returns:
            String com conteúdo CSV
        """
        import csv
        import io
        
        logs = AuditLogService.get_logs_by_tenant(
            db=db,
            tenant_id=tenant_id,
            limit=10000,
            start_date=start_date,
            end_date=end_date,
        )
        
        output = io.StringIO()
        fieldnames = [
            'id', 'user_id', 'tenant_id', 'action', 'resource_type',
            'resource_id', 'details', 'ip_address', 'user_agent', 'created_at'
        ]
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for log in logs:
            writer.writerow({
                'id': log.id,
                'user_id': log.user_id,
                'tenant_id': log.tenant_id,
                'action': log.action,
                'resource_type': log.resource_type,
                'resource_id': log.resource_id,
                'old_value': str(log.old_value) if log.old_value else '',
                'new_value': str(log.new_value) if log.new_value else '',
                'ip_address': log.ip_address or '',
                'user_agent': log.user_agent or '',
                'created_at': log.created_at.isoformat(),
            })
        
        return output.getvalue()
