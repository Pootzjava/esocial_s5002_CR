"""
eSocial Rendimentos SaaS - API Principal
Fase 2: Multi-Tenant + Billing
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time

from src.api.routers import auth, xml_upload, pdf_generation, health, billing, employees
from src.api.middleware.tenant_isolation import TenantIsolationMiddleware
from src.infrastructure.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciamento do ciclo de vida da aplicação"""
    # Startup
    print("🚀 Iniciando eSocial Rendimentos SaaS API...")
    await init_db()
    print("✅ Banco de dados inicializado")
    
    yield
    
    # Shutdown
    print("👋 Encerrando aplicação...")


app = FastAPI(
    title="eSocial Rendimentos SaaS",
    description="""
## API para emissão de Comprovante de Rendimentos
    
### Funcionalidades
- **Autenticação**: JWT tokens para segurança
- **Upload XML**: Parse automático de XML eSocial S-5002
- **Geração PDF**: Criação de comprovantes em lote
- **Multi-Tenant**: Isolamento de dados entre empresas
- **Billing**: Gestão de assinaturas com Stripe
- **Health Check**: Monitoramento da API

### Versão
**Fase 2 - Multi-Tenant + Billing**
    """,
    version="2.0.0-multi-tenant",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Middleware CORS (deve ser o primeiro)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de Isolamento Multi-Tenant (depois do CORS)
app.add_middleware(TenantIsolationMiddleware)

# Middleware de logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Roteadores
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Autenticação"])
app.include_router(xml_upload.router, prefix="/api/v1/xml", tags=["Upload XML"])
app.include_router(pdf_generation.router, prefix="/api/v1/pdf", tags=["Geração PDF"])
app.include_router(health.router, prefix="/api/v1/health", tags=["Health"])
app.include_router(billing.router, prefix="/api/v1/billing", tags=["Billing"])
app.include_router(employees.router, tags=["Funcionários"])  # já tem prefix no router


@app.get("/", tags=["Root"])
async def root():
    """Endpoint raiz com informações da API"""
    return {
        "message": "eSocial Rendimentos SaaS API",
        "version": "2.0.0-multi-tenant",
        "phase": "Fase 2 - Multi-Tenant + Billing",
        "docs": "/docs",
        "health": "/api/v1/health/status"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handler global de exceções"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_error",
            "message": str(exc),
            "path": request.url.path
        }
    )
