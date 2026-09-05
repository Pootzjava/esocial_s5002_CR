"""
Sistema de Permissões e RBAC (Role-Based Access Control)

Define permissões por papel (Admin, Manager, Viewer) e decoradores
para proteger endpoints da API.
"""
from functools import wraps
from fastapi import HTTPException, status, Request
from typing import List, Callable

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


def require_role(required_role: str):
    """
    Decorador que exige que o usuário tenha pelo menos o papel especificado.
    Considera a hierarquia de papéis (admin > manager > viewer).
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Tenta extrair request dos argumentos
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Request object not found"
                )

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

            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_permission(permission: str):
    """
    Decorador que exige que o usuário tenha uma permissão específica.
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Request object not found"
                )

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

            return await func(*args, **kwargs)
        return wrapper
    return decorator


def has_permission(role: str, permission: str) -> bool:
    """
    Verifica se um papel específico possui uma permissão.
    Útil para lógica condicional dentro dos endpoints.
    """
    role_permissions = ROLES.get(role, [])
    return permission in role_permissions
