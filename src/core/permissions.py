"""
Sistema de Permissões e RBAC (Role-Based Access Control)

Define permissões por papel (Admin, Manager, Viewer) e funções
para proteger endpoints da API usando FastAPI Depends.
"""
from fastapi import HTTPException, status, Request, Depends
from typing import List

# Classe de Roles para uso em type hints e validações
class Role:
    ADMIN = "admin"
    MANAGER = "manager"
    VIEWER = "viewer"
    HR_OPERATOR = "hr_operator"

# Definição de Papéis e Permissões
ROLES = {
    Role.ADMIN: ["read", "write", "delete", "manage_users", "billing"],
    Role.MANAGER: ["read", "write", "upload_xml", "generate_pdf"],
    Role.HR_OPERATOR: ["read", "write", "upload_xml", "generate_pdf"],
    Role.VIEWER: ["read"]
}

# Hierarquia de papéis (quem pode fazer o quê)
ROLE_HIERARCHY = {
    Role.ADMIN: 3,
    Role.MANAGER: 2,
    Role.HR_OPERATOR: 2,
    Role.VIEWER: 1
}


class PermissionDenied(Exception):
    """Exceção levantada quando usuário não tem permissão suficiente."""
    pass


def get_user_role_from_request(request: Request) -> str:
    """Extrai user_role do request state"""
    user_role = getattr(request.state, 'user_role', None)
    if not user_role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não autenticado"
        )
    return user_role


def check_admin_role(request: Request) -> str:
    """Verifica se usuário é admin"""
    user_role = get_user_role_from_request(request)
    if user_role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Acesso negado. Papel mínimo requerido: admin. Seu papel: {user_role}"
        )
    return user_role


def require_role(required_role: str):
    """
    Função que retorna uma Depends function para exigir papel mínimo.
    Uso: @router.get("/path", dependencies=[Depends(require_role("admin"))])
    """
    def check_role(request: Request) -> str:
        user_role = getattr(request.state, 'user_role', None)
        
        if not user_role:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não autenticado"
            )

        # Verifica hierarquia
        if ROLE_HIERARCHY.get(user_role, 0) < ROLE_HIERARCHY.get(required_role, 0):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso negado. Papel mínimo requerido: {required_role}. Seu papel: {user_role}"
            )
        
        return user_role
    
    return Depends(check_role)


def require_permission(permission: str):
    """
    Função que retorna uma Depends function para exigir permissão específica.
    """
    def check_permission(request: Request):
        user_role = getattr(request.state, 'user_role', None)
        
        if not user_role:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não autenticado"
            )

        user_permissions = ROLES.get(user_role, [])
        
        if permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso negado. Permissão '{permission}' requerida."
            )
        
        return user_role
    
    return Depends(check_permission)


def has_permission(role: str, permission: str) -> bool:
    """
    Verifica se um papel específico possui uma permissão.
    Útil para lógica condicional dentro dos endpoints.
    """
    role_permissions = ROLES.get(role, [])
    return permission in role_permissions
