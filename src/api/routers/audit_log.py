"""
Router de Audit Log para endpoints de consulta e exportação de logs de auditoria.
Conforme requisitos da Fase 3: Enterprise Ready.
"""
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from src.infrastructure.database import get_db
from src.api.dependencies import get_current_user_id, get_current_tenant_id, require_role
from src.services.audit_log import AuditLogService

router = APIRouter(prefix="/audit", tags=["Audit Logs"])


@router.get("/logs")
def get_audit_logs(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    user_id: Optional[int] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_current_tenant_id),
    current_user_id: int = Depends(get_current_user_id),
    user_role: str = Depends(require_role(["admin", "auditor"])),
):
    """
    Recupera logs de auditoria do tenant com filtros opcionais.
    Requer papel de Admin ou Auditor.
    """
    logs = AuditLogService.get_logs_by_tenant(
        db=db,
        tenant_id=tenant_id,
        limit=limit,
        offset=offset,
        action_filter=action,
        resource_type_filter=resource_type,
        user_id_filter=user_id,
        start_date=start_date,
        end_date=end_date,
    )
    
    return {
        "total": len(logs),
        "limit": limit,
        "offset": offset,
        "logs": [
            {
                "id": log.id,
                "user_id": log.user_id,
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "details": log.details,
                "ip_address": log.ip_address,
                "created_at": log.created_at.isoformat(),
            }
            for log in logs
        ],
    }


@router.get("/logs/export")
def export_audit_logs(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_current_tenant_id),
    current_user_id: int = Depends(get_current_user_id),
    user_role: str = Depends(require_role(["admin"])),
):
    """
    Exporta logs de auditoria em formato CSV.
    Requer papel de Admin.
    """
    csv_content = AuditLogService.export_logs_to_csv(
        db=db,
        tenant_id=tenant_id,
        start_date=start_date,
        end_date=end_date,
    )
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=audit_logs.csv"
        },
    )
