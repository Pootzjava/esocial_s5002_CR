"""
Router de Funcionários (Employees)
Gerencia CRUD de funcionários com isolamento multi-tenant.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field

from src.infrastructure.database import get_db
from src.domain.models_orm import Employee, Tenant
from src.core.permissions import require_role, Role

router = APIRouter(prefix="/api/v1/employees", tags=["employees"])


class EmployeeCreate(BaseModel):
    cpf: str = Field(..., description="CPF do funcionário")
    name: str = Field(..., description="Nome completo do funcionário")
    email: Optional[str] = Field(None, description="E-mail do funcionário")


class EmployeeResponse(BaseModel):
    id: int
    tenant_id: int
    cpf: str
    name: str
    email: Optional[str] = None
    
    class Config:
        from_attributes = True


@router.get("", response_model=List[EmployeeResponse])
async def list_employees(
    request: Request,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Lista todos os funcionários do tenant autenticado.
    Requer autenticação e role mínimo: viewer.
    """
    # Middleware deve ter injetado tenant_id no request.state
    tenant_id = getattr(request.state, 'tenant_id', None)
    
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não autenticado ou tenant_id não encontrado"
        )
    
    employees = db.query(Employee).filter(
        Employee.tenant_id == tenant_id
    ).offset(skip).limit(limit).all()
    
    return employees


@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Obtém detalhes de um funcionário específico.
    Requer autenticação e role mínimo: viewer.
    """
    tenant_id = request.state.tenant_id
    
    employee = db.query(Employee).filter(
        Employee.id == employee_id,
        Employee.tenant_id == tenant_id
    ).first()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Funcionário {employee_id} não encontrado neste tenant"
        )
    
    return employee


@router.post("", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
    employee_data: EmployeeCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Cria um novo funcionário no tenant autenticado.
    Requer role: manager ou admin.
    """
    # Verificar permissão
    user_role = request.state.user_role
    if user_role not in [Role.ADMIN, Role.MANAGER, Role.HR_OPERATOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão negada. Apenas managers, hr_operators ou admins podem criar funcionários."
        )
    
    tenant_id = request.state.tenant_id
    
    # Validar se CPF já existe neste tenant
    existing = db.query(Employee).filter(
        Employee.cpf == employee_data.cpf,
        Employee.tenant_id == tenant_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CPF já cadastrado neste tenant"
        )
    
    employee = Employee(
        tenant_id=tenant_id,
        cpf=employee_data.cpf,
        name=employee_data.name,
        email=employee_data.email
    )
    
    db.add(employee)
    db.commit()
    db.refresh(employee)
    
    return employee


@router.put("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: int,
    employee_data: EmployeeCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Atualiza dados de um funcionário.
    Requer role: manager ou admin.
    """
    user_role = request.state.user_role
    if user_role not in [Role.ADMIN, Role.MANAGER, Role.HR_OPERATOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão negada."
        )
    
    tenant_id = request.state.tenant_id
    
    employee = db.query(Employee).filter(
        Employee.id == employee_id,
        Employee.tenant_id == tenant_id
    ).first()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Funcionário não encontrado"
        )
    
    # Atualizar campos
    employee.cpf = employee_data.cpf
    employee.name = employee_data.name
    employee.email = employee_data.email
    
    db.commit()
    db.refresh(employee)
    
    return employee


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(
    employee_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Remove um funcionário.
    Requer role: admin.
    """
    user_role = request.state.user_role
    if user_role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas admins podem remover funcionários."
        )
    
    tenant_id = request.state.tenant_id
    
    employee = db.query(Employee).filter(
        Employee.id == employee_id,
        Employee.tenant_id == tenant_id
    ).first()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Funcionário não encontrado"
        )
    
    db.delete(employee)
    db.commit()
    
    return None
