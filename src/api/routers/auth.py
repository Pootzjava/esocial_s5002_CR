"""
Router de Autenticação - JWT Token
Fase 1: MVP Core
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Optional
import os

# Configurações
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter()

# Contexto de criptografia
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class Token(BaseModel):
    """Modelo de resposta do token"""
    access_token: str
    token_type: str
    expires_in: int


class TokenData(BaseModel):
    """Dados do token decodificado"""
    username: Optional[str] = None
    tenant_id: Optional[str] = None


class UserCreate(BaseModel):
    """Modelo para criação de usuário"""
    username: str
    email: str
    password: str
    tenant_id: str


class UserResponse(BaseModel):
    """Modelo de resposta do usuário"""
    id: int
    username: str
    email: str
    tenant_id: str
    is_active: bool


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha plain text corresponde ao hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Gera hash da senha"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Cria token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    """Valida e retorna o usuário atual do token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        tenant_id: str = payload.get("tenant_id")
        
        if username is None:
            raise credentials_exception
        
        return TokenData(username=username, tenant_id=tenant_id)
    
    except JWTError:
        raise credentials_exception


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate):
    """
    Registra um novo usuário
    
    - **username**: Nome de usuário único
    - **email**: Email válido
    - **password**: Senha (mínimo 8 caracteres)
    - **tenant_id**: ID do tenant (empresa)
    """
    # Em produção, validar se usuário já existe no banco
    # Aqui é apenas mock para MVP
    
    if len(user.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters"
        )
    
    # Mock de resposta
    return UserResponse(
        id=1,
        username=user.username,
        email=user.email,
        tenant_id=user.tenant_id,
        is_active=True
    )


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Realiza login e retorna token JWT
    
    - **username**: Nome de usuário ou email
    - **password**: Senha do usuário
    """
    # Em produção, buscar usuário no banco
    # Mock para MVP - aceitar qualquer usuário com senha >= 8 chars
    
    if len(form_data.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Criar token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": form_data.username,
            "tenant_id": "tenant-mock"
        },
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: TokenData = Depends(get_current_user)):
    """
    Retorna informações do usuário autenticado
    """
    # Mock de resposta
    return UserResponse(
        id=1,
        username=current_user.username,
        email=f"{current_user.username}@example.com",
        tenant_id=current_user.tenant_id,
        is_active=True
    )
