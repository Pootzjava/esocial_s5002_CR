"""
Middleware de Isolamento Multi-Tenant

Garante que todas as requisições sejam escopadas ao tenant correto
baseado no token JWT do usuário autenticado.
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, DispatchFunction
from jose import jwt, JWTError
from typing import Optional
import os

JWT_SECRET = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"


class TenantIsolationMiddleware(BaseHTTPMiddleware):
    """
    Middleware que extrai o tenant_id do token JWT e garante
    que o usuário só acesse dados do seu próprio tenant.
    """

    async def dispatch(self, request: Request, call_next: DispatchFunction):
        # Rotas públicas que não requerem autenticação
        # Usamos paths exatos ou prefixos específicos terminados em /
        public_paths = [
            "/health", "/docs", "/openapi.json", "/redoc", "/",
            "/api/v1/auth/register", 
            "/api/v1/billing/plans", 
            "/api/v1/billing/webhook"
        ]
        
        # Verifica se é rota pública - matching exato ou prefixo com /
        is_public = False
        request_path = request.url.path
        
        for public_path in public_paths:
            # Match exato
            if request_path == public_path:
                is_public = True
                break
            # Match de prefixo (para sub-paths)
            if request_path.startswith(public_path + "/"):
                is_public = True
                break
        
        if is_public:
            return await call_next(request)

        # Tenta extrair o token do header Authorization
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Token de autenticação ausente ou inválido"}
            )

        token = auth_header.split(" ")[1]

        try:
            # Decodifica o token para extrair o tenant_id
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            tenant_id = payload.get("tenant_id")
            user_role = payload.get("role", "user")

            if not tenant_id:
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "Tenant ID não encontrado no token"}
                )

            # Injeta o tenant_id e role no estado da requisição para uso nos routers
            request.state.tenant_id = tenant_id
            request.state.user_role = user_role
            request.state.user_id = payload.get("sub")

        except JWTError:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Token inválido ou expirado"}
            )

        # Chama o próximo middleware/endpoint
        response = await call_next(request)
        return response
