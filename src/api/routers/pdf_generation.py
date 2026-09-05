"""
Router de Geração de PDF - Comprovante de Rendimentos
Fase 1: MVP Core
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os
import uuid

from src.api.routers.auth import get_current_user, TokenData

router = APIRouter()

# Diretório para PDFs gerados
PDF_DIR = os.getenv("PDF_DIR", "/tmp/esocial_pdfs")


def ensure_pdf_dir():
    """Garante que o diretório de PDFs existe"""
    os.makedirs(PDF_DIR, exist_ok=True)


class PDFGenerationRequest(BaseModel):
    """Requisição para geração de PDF"""
    employee_ids: Optional[List[str]] = None
    year: int
    include_qr_code: bool = True
    template: str = "standard"


class PDFGenerationResult(BaseModel):
    """Resultado da geração do PDF"""
    id: str
    status: str
    file_path: Optional[str]
    employees_count: int
    created_at: datetime
    download_url: Optional[str]


class BatchPDFRequest(BaseModel):
    """Requisição para geração em lote"""
    year: int
    all_employees: bool = True
    employee_ids: Optional[List[str]] = None


@router.post("/generate", response_model=PDFGenerationResult)
async def generate_pdf(
    request: PDFGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Gera PDF do comprovante de rendimentos
    
    - **employee_ids**: Lista de IDs de funcionários (opcional)
    - **year**: Ano de referência
    - **include_qr_code**: Incluir QR Code de validação
    - **template**: Modelo do PDF (standard, simplified, detailed)
    """
    ensure_pdf_dir()
    
    # Validar ano
    current_year = datetime.now().year
    if request.year < 2020 or request.year > current_year + 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Year must be between 2020 and {current_year + 1}"
        )
    
    # Gerar ID único
    pdf_id = str(uuid.uuid4())
    filename = f"comprovante_{pdf_id}.pdf"
    file_path = os.path.join(PDF_DIR, filename)
    
    # Mock: Em produção, gerar PDF real
    # Aqui criamos um arquivo vazio para simular
    with open(file_path, 'w') as f:
        f.write(f"PDF Mock - Year: {request.year} - Employees: {len(request.employee_ids or [])}")
    
    return PDFGenerationResult(
        id=pdf_id,
        status="completed",
        file_path=file_path,
        employees_count=len(request.employee_ids or []),
        created_at=datetime.utcnow(),
        download_url=f"/api/v1/pdf/download/{pdf_id}"
    )


@router.post("/batch", response_model=PDFGenerationResult)
async def generate_batch_pdf(
    request: BatchPDFRequest,
    background_tasks: BackgroundTasks,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Gera PDF em lote para múltiplos funcionários
    
    - **year**: Ano de referência
    - **all_employees**: Gerar para todos os funcionários
    - **employee_ids**: Lista específica de IDs (se all_employees=False)
    """
    ensure_pdf_dir()
    
    # Validar ano
    current_year = datetime.now().year
    if request.year < 2020 or request.year > current_year + 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Year must be between 2020 and {current_year + 1}"
        )
    
    # Gerar ID único
    pdf_id = str(uuid.uuid4())
    filename = f"lote_{request.year}_{pdf_id}.pdf"
    file_path = os.path.join(PDF_DIR, filename)
    
    # Mock: Simular geração em lote
    employees_count = 10 if request.all_employees else len(request.employee_ids or [])
    
    with open(file_path, 'w') as f:
        f.write(f"Batch PDF Mock - Year: {request.year} - Employees: {employees_count}")
    
    return PDFGenerationResult(
        id=pdf_id,
        status="completed",
        file_path=file_path,
        employees_count=employees_count,
        created_at=datetime.utcnow(),
        download_url=f"/api/v1/pdf/download/{pdf_id}"
    )


@router.get("/download/{pdf_id}")
async def download_pdf(
    pdf_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Baixa o PDF gerado
    
    - **pdf_id**: ID do PDF gerado
    """
    ensure_pdf_dir()
    
    filename = f"comprovante_{pdf_id}.pdf"
    file_path = os.path.join(PDF_DIR, filename)
    
    if not os.path.exists(file_path):
        # Tentar como batch
        batch_filename = f"lote_*_{pdf_id}.pdf"
        import glob
        matches = glob.glob(os.path.join(PDF_DIR, f"lote_*_{pdf_id}.pdf"))
        if matches:
            file_path = matches[0]
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="PDF not found"
            )
    
    return FileResponse(
        path=file_path,
        media_type='application/pdf',
        filename=os.path.basename(file_path)
    )


@router.get("/status/{pdf_id}", response_model=PDFGenerationResult)
async def get_generation_status(
    pdf_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Verifica o status da geração do PDF
    
    - **pdf_id**: ID do PDF sendo gerado
    """
    ensure_pdf_dir()
    
    # Mock: Sempre retorna completed no MVP
    return PDFGenerationResult(
        id=pdf_id,
        status="completed",
        file_path=None,
        employees_count=1,
        created_at=datetime.utcnow(),
        download_url=f"/api/v1/pdf/download/{pdf_id}"
    )


@router.delete("/{pdf_id}")
async def delete_pdf(
    pdf_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Remove um PDF gerado
    
    - **pdf_id**: ID do PDF a ser removido
    """
    ensure_pdf_dir()
    
    # Mock: Simular deleção
    return {"message": "PDF deleted successfully"}
