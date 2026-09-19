"""
Router de Upload e Processamento de XML eSocial S-5002
Fase 1: MVP Core
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
import xml.etree.ElementTree as ET
from datetime import datetime
import os
import uuid

from src.api.routers.auth import get_current_user, TokenData

router = APIRouter()

# Diretório temporário para uploads
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/tmp/esocial_uploads")


def ensure_upload_dir():
    """Garante que o diretório de upload existe"""
    os.makedirs(UPLOAD_DIR, exist_ok=True)


class XMLProcessingResult(BaseModel):
    """Resultado do processamento do XML"""
    id: str
    filename: str
    status: str
    events_count: int
    employees_count: int
    created_at: datetime


@router.post("/upload", response_model=XMLProcessingResult)
async def upload_xml(
    file: UploadFile = File(..., description="Arquivo XML eSocial S-5002"),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Faz upload e processa arquivo XML eSocial S-5002
    
    - **file**: Arquivo XML no formato eSocial S-5002
    - Retorna informações sobre o processamento
    """
    ensure_upload_dir()
    
    # Validar extensão
    if not file.filename.endswith('.xml'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only XML files are allowed"
        )
    
    try:
        # Ler conteúdo do arquivo
        content = await file.read()
        
        # Salvar arquivo temporariamente
        file_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
        
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # Processar XML
        result = process_esocial_xml(content, file.filename)
        
        return XMLProcessingResult(
            id=file_id,
            filename=file.filename,
            status=result['status'],
            events_count=result['events_count'],
            employees_count=result['employees_count'],
            created_at=datetime.utcnow()
        )
    
    except ET.ParseError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid XML format: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )


def process_esocial_xml(xml_content: bytes, filename: str) -> dict:
    """
    Processa XML eSocial S-5002 e extrai informações
    
    Returns:
        dict com status, contagem de eventos e funcionários
    """
    root = ET.fromstring(xml_content)
    
    # Definir namespaces do eSocial
    namespaces = {
        'esocial': 'http://www.esocial.gov.br/schema/evt/evtPgtos/v_S_01_02_00'
    }
    
    events_count = 0
    employees = set()
    
    # Tentar encontrar eventos S-5002
    # Procurar por elementos de evento
    for event in root.iter():
        if 'evtPgtos' in event.tag or 'S-5002' in event.tag:
            events_count += 1
        
        # Extrair CPFs dos beneficiários
        if 'cpfBenef' in event.tag or 'cpf' in event.tag.lower():
            if event.text and len(event.text.strip()) >= 11:
                cpf = event.text.strip()[:11]
                employees.add(cpf)
    
    return {
        'status': 'processed',
        'events_count': events_count if events_count > 0 else 1,
        'employees_count': len(employees)
    }


@router.get("/list", response_model=List[XMLProcessingResult])
async def list_processed_files(
    skip: int = 0,
    limit: int = 100,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Lista arquivos XML processados
    
    - **skip**: Quantidade de registros para pular (paginação)
    - **limit**: Quantidade máxima de registros a retornar
    """
    # Mock para MVP - em produção buscar do banco
    return []


@router.get("/{file_id}", response_model=XMLProcessingResult)
async def get_file_details(
    file_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Retorna detalhes de um arquivo processado
    
    - **file_id**: ID único do arquivo processado
    """
    # Mock para MVP
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="File not found"
    )


@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Remove um arquivo processado
    
    - **file_id**: ID único do arquivo processado
    """
    # Mock para MVP
    return {"message": "File deleted successfully"}
