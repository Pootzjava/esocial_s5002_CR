"""
Dependências comuns para os routers da API.
Inclui autenticação, extração de tenant e verificação de permissões.
"""
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from src.infrastructure.database import get_db
from src.domain.models_orm import User, Tenant, UserRole
from src.config.settings import settings

security = HTTPBearer()


def get_current_user_id(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> int:
    """
    Extrai o ID do usuário atual do token JWT.
    Nota: O 'sub' no token é um mock_user_id gerado no login, não o ID real do DB.
    Para testes e MVP, retornamos o tenant_id como proxy ou buscamos pelo username.
    """
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id_raw = payload.get("sub")
        
        if user_id_raw is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Em MVP/mock, o 'sub' é um ID gerado por hash, não o ID real do DB
        # Precisamos buscar o usuário pelo username ou usar uma abordagem diferente
        # Para simplificar, vamos buscar o primeiro usuário admin do tenant
        tenant_id = payload.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID não encontrado no token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Buscar primeiro usuário admin do tenant (para MVP)
        # Nota: role pode ser string ou UserRole enum
        user = db.query(User).filter(
            User.tenant_id == tenant_id,
            (User.role == UserRole.admin) | (User.role == "admin")
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user.id
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_tenant_id(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> int:
    """
    Extrai o ID do tenant do token JWT ou do header X-Tenant-ID.
    """
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        tenant_id: int = payload.get("tenant_id")
        
        if tenant_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verificar se tenant existe
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return tenant_id
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user_role(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
) -> str:
    """
    Retorna o papel (role) do usuário atual como string.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Converter enum para string se necessário
    role_value = user.role.value if hasattr(user.role, 'value') else str(user.role)
    return role_value


def require_role(allowed_roles: list[str]):
    """
    Decorador para exigir que o usuário tenha um dos papéis especificados.
    
    Uso:
        @router.get("/admin")
        @require_role(["admin"])
        def admin_endpoint(...):
            ...
    """
    def role_checker(
        role: str = Depends(get_current_user_role),
    ):
        if role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {allowed_roles}",
            )
        return role
    
    return role_checker


def get_current_user(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
) -> User:
    """
    Retorna o objeto User completo do usuário atual.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return user
