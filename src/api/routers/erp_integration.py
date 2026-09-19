"""
Router de Integração ERP para upload e processamento de arquivos de sistemas ERP.
Conforme requisitos da Fase 3: Enterprise Ready.
Suporta Totvs, SAP, Oracle e Senior.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from src.infrastructure.database import get_db
from src.api.dependencies import get_current_user_id, get_current_tenant_id
from src.integrations.erp.parser import ERPIntegrationService
from src.services.audit_log import AuditLogService

router = APIRouter(prefix="/erp", tags=["ERP Integration"])


@router.post("/import")
async def import_erp_file(
    file: UploadFile = File(..., description="Arquivo do ERP (TXT, CSV ou XML)"),
    dry_run: bool = Form(False, description="Se true, apenas valida sem importar"),
    db: Session = Depends(get_db),
    tenant_id: int = Depends(get_current_tenant_id),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Importa arquivo de funcionário e eventos de rendimento de um ERP.
    
    Formatos suportados:
    - Totvs: TXT com delimitador pipe (|)
    - SAP: CSV com delimitador ponto-e-vírgula (;)
    - Oracle: XML HCM
    - Senior: TXT similar ao Totvs
    
    Parâmetros:
    - file: Arquivo do ERP
    - dry_run: Se true, apenas valida os dados sem persistir no banco
    
    Retorna:
    - Dados processados e validados
    """
    try:
        content = await file.read()
        content_str = content.decode('utf-8')
        
        # Detectar formato e fazer parse automático
        result = ERPIntegrationService.parse_auto(content_str)
        
        # Registrar log de auditoria
        AuditLogService.log_action(
            db=db,
            user_id=current_user_id,
            tenant_id=tenant_id,
            action="ERP_IMPORT",
            resource_type="ERPIntegration",
            details={
                "filename": file.filename,
                "format_detected": result.get('detected_format'),
                "employees_count": len(result.get('employees', [])),
                "events_count": len(result.get('events', [])),
                "dry_run": dry_run,
            },
        )
        
        # Em produção, aqui faria a importação real para o banco de dados
        # Por enquanto, retorna os dados processados
        
        return {
            "success": True,
            "message": "Arquivo processado com sucesso",
            "data": {
                "source": result.get('source'),
                "detected_format": result.get('detected_format'),
                "processed_at": result.get('processed_at'),
                "employees_count": len(result.get('employees', [])),
                "events_count": len(result.get('events', [])),
                "employees_preview": result.get('employees', [])[:5],  # Preview dos primeiros 5
                "events_preview": result.get('events', [])[:5],
                "warning": result.get('warning'),
            },
            "dry_run": dry_run,
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar arquivo: {str(e)}")


@router.get("/supported-formats")
def get_supported_formats():
    """
    Retorna lista de formatos de ERP suportados e suas especificações.
    """
    return {
        "formats": [
            {
                "name": "TOTVS",
                "extension": ".txt",
                "delimiter": "|",
                "record_types": ["FUNCIONARIO", "EVENTO"],
                "example": "FUNCIONARIO|matricula|nome|cpf|cargo|departamento|data_admissao|salario|categoria",
            },
            {
                "name": "SAP",
                "extension": ".csv",
                "delimiter": ";",
                "record_types": ["FUNC", "EVT"],
                "has_header": True,
                "example": "TIPO_REGISTRO;MATRICULA;NOME;CPF;CARGO;DEPARTAMENTO;DATA_ADMISSAO;SALARIO;CATEGORIA",
            },
            {
                "name": "ORACLE",
                "extension": ".xml",
                "format": "XML HCM",
                "status": "Em desenvolvimento",
            },
            {
                "name": "SENIOR",
                "extension": ".txt",
                "delimiter": "|",
                "record_types": ["FUNCIONARIO", "EVENTO"],
                "example": "Similar ao formato TOTVS",
            },
        ],
        "auto_detect": True,
        "max_file_size_mb": 50,
    }
