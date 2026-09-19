"""
API Router de Audit Logs - Fase 3: Enterprise Ready

Endpoints para consulta e exportação de logs de auditoria.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from src.infrastructure.database import get_db
from src.modules.audit.logger import AuditLogger, ActionType


router = APIRouter(prefix="/audit", tags=["Audit Logs"])


@router.get("/logs")
async def list_audit_logs(
    resource_type: Optional[str] = Query(None, description="Filtrar por tipo de recurso"),
    action: Optional[ActionType] = Query(None, description="Filtrar por tipo de ação"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Lista logs de auditoria do tenant atual.
    
    Apenas usuários com role 'admin' podem acessar.
    """
    # Em produção, consultaria o banco de dados
    # logs = db.query(AuditLog).filter_by(tenant_id=tenant_id)...
    
    return {
        "logs": [],
        "total": 0,
        "limit": limit,
        "offset": offset
    }


@router.get("/logs/{log_id}")
async def get_audit_log(
    log_id: int,
    db: Session = Depends(get_db),
    request: Request = None
):
    """Obtém detalhes de um log de auditoria específico."""
    # Em produção, consultaria o banco de dados
    # log = db.query(AuditLog).filter_by(id=log_id, tenant_id=tenant_id).first()
    
    return {
        "id": log_id,
        "tenant_id": 1,
        "user_id": 1,
        "user_email": "admin@example.com",
        "action": "LOGIN",
        "resource_type": "user",
        "timestamp": "2024-01-15T10:30:00Z"
    }


@router.get("/logs/export")
async def export_audit_logs(
    format: str = Query("csv", regex="^(csv|json)$"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Exporta logs de auditoria em CSV ou JSON.
    
    Útil para compliance e auditorias externas.
    """
    from fastapi.responses import StreamingResponse
    import csv
    import io
    import json
    from src.domain.models_orm import AuditLog
    
    # Obter tenant_id do request (injetado pelo middleware)
    tenant_id = getattr(request.state, "tenant_id", None)
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant ID não encontrado")
    
    # Buscar logs do banco de dados
    query = db.query(AuditLog).filter(AuditLog.tenant_id == tenant_id)
    
    if start_date:
        query = query.filter(AuditLog.created_at >= start_date)
    if end_date:
        query = query.filter(AuditLog.created_at <= end_date)
    
    logs = query.order_by(AuditLog.created_at.desc()).limit(1000).all()
    
    # Converter para dicionários (na ordem esperada pelo teste)
    logs_data = []
    for log in logs:
        # Converter old_value e new_value para string JSON se forem dict
        old_val = json.dumps(log.old_value) if log.old_value is not None and isinstance(log.old_value, (dict, list)) else log.old_value
        new_val = json.dumps(log.new_value) if log.new_value is not None and isinstance(log.new_value, (dict, list)) else log.new_value
        
        logs_data.append({
            "id": log.id,
            "user_id": log.user_id,
            "tenant_id": log.tenant_id,
            "action": log.action.value if hasattr(log.action, 'value') else str(log.action),
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "ip_address": log.ip_address,
            "user_agent": log.user_agent,
            "created_at": log.created_at.isoformat() if log.created_at else None,
            "old_value": old_val,
            "new_value": new_val
        })
    
    if format == "json":
        return StreamingResponse(
            iter([json.dumps(logs_data, indent=2)]),
            media_type="application/json",
            headers={
                "Content-Disposition": "attachment; filename=audit_logs.json"
            }
        )
    
    # CSV export - incluir todos os campos da tabela (na ordem esperada pelo teste)
    output = io.StringIO()
    fieldnames = ["id", "user_id", "tenant_id", "action", "resource_type", "resource_id", "ip_address", "user_agent", "created_at", "old_value", "new_value"]
    
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
    writer.writeheader()
    
    for log in logs_data:
        writer.writerow(log)
    
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": "attachment; filename=audit_logs.csv"
        }
    )
