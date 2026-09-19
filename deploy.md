# 🚀 Guia de Implantação e Uso - eSocial Rendimentos SaaS™

Este documento cobre todo o ciclo de vida da aplicação: desde o ambiente de desenvolvimento local até a implantação em produção com Kubernetes, passando por testes, build e operação diária.

**Versão do Documento:** 1.0  
**Última Atualização:** Outubro 2023  
**Status do Projeto:** ✅ Todas as 6 Fases Implementadas

---

## 📋 Índice

1. [Pré-requisitos](#-pré-requisitos)
2. [Ambiente de Desenvolvimento Local](#️-ambiente-de-desenvolvimento-local)
3. [Testes Automatizados](#-testes-automatizados)
4. [Build para Produção](#️-build-para-produção)
5. [Implantação (Kubernetes)](#-implantação-kubernetes)
6. [Uso do Sistema (Guia Rápido)](#-uso-do-sistema-guia-rápido)
7. [Suporte e Monitoramento](#-suporte-e-monitoramento)
8. [Solução de Problemas Comuns](#-solução-de-problemas-comuns)

---

## 📋 Pré-requisitos

Antes de começar, certifique-se de ter as seguintes ferramentas instaladas:

*   **Python:** Versão 3.9 ou superior
*   **Node.js:** Versão 18.x ou superior (LTS recomendado)
*   **npm/yarn:** Gerenciador de pacotes Node
*   **Docker & Docker Compose:** Para containerização de serviços locais (DB, Redis)
*   **Kubectl:** CLI para gerenciamento de clusters Kubernetes
*   **Helm:** Gerenciador de pacotes para Kubernetes (opcional, mas recomendado)
*   **Stripe CLI:** Para testes locais de webhooks de pagamento (`stripe listen`)
*   **Git:** Controle de versão

---

## 1. 🛠️ Ambiente de Desenvolvimento Local

Siga estes passos para configurar o ambiente de desenvolvimento completo.

### Passo 1: Configurar o Backend (Python/FastAPI)

```bash
# 1. Navegue até a raiz do projeto
cd /workspace

# 2. Crie um ambiente virtual Python
python -m venv venv

# 3. Ative o ambiente virtual
# Linux/Mac:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 4. Instale as dependências do backend
pip install -r requirements.txt

# 5. Configure as variáveis de ambiente
cp config/settings.env .env

# ⚠️ IMPORTANTE: Edite o arquivo .env e ajuste as seguintes chaves para desenvolvimento:
# DATABASE_URL=postgresql://user:password@localhost:5432/esocial_dev
# JWT_SECRET=sua-chave-secreta-para-dev
# STRIPE_SECRET_KEY=sk_test_... (use chaves de teste do Stripe)
# STRIPE_WEBHOOK_SECRET=whsec_...

# 6. Inicie o banco de dados local (se ainda não estiver rodando)
docker-compose up -d db redis

# 7. Execute as migrations para criar as tabelas no banco de dados
# Nota: Certifique-se de que o comando alembic está disponível no PATH ou use python -m alembic
alembic upgrade head

# 8. Inicie o servidor de desenvolvimento do FastAPI
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

O backend estará disponível em: `http://localhost:8000`  
Documentação Swagger: `http://localhost:8000/docs`

### Passo 2: Configurar o Frontend (Next.js)

Abra um **novo terminal** (mantenha o backend rodando no anterior):

```bash
# 1. Navegue até o diretório do frontend
cd /workspace/frontend

# 2. Instale as dependências do Node
npm install

# 3. Configure as variáveis de ambiente
cp .env.local.example .env.local

# ⚠️ IMPORTANTE: Edite frontend/.env.local:
# NEXT_PUBLIC_API_URL=http://localhost:8000
# NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...

# 4. Inicie o servidor de desenvolvimento do Next.js
npm run dev
```

O frontend estará disponível em: `http://localhost:3000`

### Passo 3: Validar Instalação

1.  Acesse `http://localhost:3000` no seu navegador.
2.  Clique em "Criar Conta" e registre um novo usuário.
3.  Faça login e verifique se o Dashboard carrega corretamente.
4.  Tente fazer upload de um XML de teste (disponível em `tests/fixtures/`).

---

## 2. 🧪 Testes Automatizados

A suíte de testes cobre todas as 6 fases do projeto, garantindo estabilidade e regressão zero.

### Executar Testes do Backend

```bash
# Ative o ambiente virtual do backend primeiro
source venv/bin/activate

# Execute todos os testes unitários e de integração
pytest tests/ -v --cov=src --cov-report=html

# Execute apenas testes rápidos (unitários)
pytest tests/unit/ -v

# Execute apenas testes de integração (requer DB rodando)
pytest tests/integration/ -v
```

*   **Cobertura Esperada:** >85%
*   **Tempo Médio de Execução:** ~2-3 minutos
*   **Relatório HTML:** Abra `htmlcov/index.html` no navegador após a execução.

### Executar Testes do Frontend

```bash
cd frontend

# Executar testes unitários e de componentes
npm run test

# Executar testes com watch mode (desenvolvimento)
npm run test:watch
```

> **Status Atual:** ✅ Todos os testes críticos de negócio (Auth, Upload, PDF, Billing, Multi-tenant, Audit Logs) estão passando.

---

## 3. 🏗️ Build para Produção

Gere as imagens Docker otimizadas para implantação.

### Backend (API FastAPI)

```bash
# Na raiz do projeto
docker build -t esocial-rendimentos-api:latest -f docker/Dockerfile.api .

# Opcional: Push para registry (Docker Hub, ECR, GCR)
docker tag esocial-rendimentos-api:latest seu-registry/esocial-rendimentos-api:v1.0.0
docker push seu-registry/esocial-rendimentos-api:v1.0.0
```

### Frontend (Next.js)

```bash
# Na raiz do projeto
docker build -t esocial-rendimentos-web:latest -f docker/Dockerfile.web .

# Opcional: Push para registry
docker tag esocial-rendimentos-web:latest seu-registry/esocial-rendimentos-web:v1.0.0
docker push seu-registry/esocial-rendimentos-web:v1.0.0
```

---

## 4. 🌍 Implantação (Kubernetes)

Para ambientes de Staging e Produção, utilizamos manifests Kubernetes preparados na **Fase 4**.

### Passo 1: Configurar Cluster e Secrets

Certifique-se de estar conectado ao cluster correto (`kubectl config use-context ...`).

```bash
# 1. Criar namespace dedicado
kubectl create namespace esocial-prod

# 2. Criar Secrets sensíveis (NUNCA commitar no Git)
# Substitua os valores pelos seus segredos reais
kubectl create secret generic app-secrets \
  --from-literal=DATABASE_URL="postgresql://user:pass@db-host.prod:5432/esocial_prod" \
  --from-literal=JWT_SECRET="sua-chave-secreta-forte-gerada-com-openssl" \
  --from-literal=STRIPE_SECRET_KEY="sk_live_..." \
  --from-literal=STRIPE_WEBHOOK_SECRET="whsec_..." \
  --from-literal=ENCRYPTION_KEY="chave-32-bytes-para-criptografia" \
  -n esocial-prod

# 3. (Opcional) Criar secret para TLS/SSL se não usar gerenciador automático
kubectl create secret tls tls-secret \
  --cert=path/to/tls.crt \
  --key=path/to/tls.key \
  -n esocial-prod
```

### Passo 2: Aplicar Configurações de Infraestrutura

```bash
# 1. Aplicar ConfigMaps (configurações não sensíveis)
kubectl apply -f k8s/configmap.yaml -n esocial-prod

# 2. Aplicar Deployments (API e Web)
kubectl apply -f k8s/deployment-api.yaml -n esocial-prod
kubectl apply -f k8s/deployment-web.yaml -n esocial-prod

# 3. Aplicar Serviços (Load Balancers internos)
kubectl apply -f k8s/service-api.yaml -n esocial-prod
kubectl apply -f k8s/service-web.yaml -n esocial-prod

# 4. Aplicar Ingress (Roteamento externo e SSL)
kubectl apply -f k8s/ingress.yaml -n esocial-prod

# 5. Aplicar Auto-scaling Horizontal (HPA)
kubectl apply -f k8s/hpa-api.yaml -n esocial-prod
kubectl apply -f k8s/hpa-web.yaml -n esocial-prod
```

### Passo 3: Verificar Status da Implantação

```bash
# Verificar se todos os Pods estão rodando (STATUS: Running)
kubectl get pods -n esocial-prod

# Verificar Serviços e IPs externos
kubectl get svc -n esocial-prod

# Verificar logs em tempo real da API
kubectl logs -f deployment/api-esocial -n esocial-prod

# Verificar eventos do namespace (útil para debug de erros de agendamento)
kubectl get events -n esocial-prod --sort-by='.lastTimestamp'
```

### Passo 4: Escalar Manualmente (Se necessário)

```bash
# Escalar a API para 10 réplicas durante pico de processamento
kubectl scale deployment/api-esocial --replicas=10 -n esocial-prod
```

---

## 5. 💻 Uso do Sistema (Guia Rápido)

Guia passo-a-passo para usuários finais e administradores.

### 1. Acesso Inicial e Criação de Conta
*   Acesse a URL pública (ex: `https://rendimentos.suaempresa.com`).
*   Clique em **"Começar Agora"** ou **"Criar Conta"**.
*   Preencha Nome, E-mail Corporativo e Senha.
*   **Nota:** O primeiro usuário criado em um novo domínio torna-se automaticamente o **Admin do Tenant**.

### 2. Configuração da Empresa (Tenant)
*   No Dashboard, navegue até **Configurações > Minha Empresa**.
*   Preencha:
    *   Razão Social e Nome Fantasia.
    *   CNPJ (validado automaticamente).
    *   Endereço Completo.
    *   Certificado Digital (upload do arquivo .pfx ou configuração de token A3 para assinatura futura).

### 3. Assinatura e Gestão de Planos (Billing)
*   Vá em **Faturamento > Planos** no menu lateral.
*   Visualize os planos disponíveis (Free, Starter, Professional, Enterprise).
*   Selecione o plano desejado e clique em **Assinar**.
*   Você será redirecionado para o Checkout Seguro do Stripe.
*   Após o pagamento, o webhook atualizará automaticamente o status da conta para `active`.
*   **Gestão:** É possível fazer upgrade, downgrade ou cancelar a assinatura a qualquer momento neste painel.

### 4. Importação de Dados (Upload XML eSocial)
*   Navegue até **Processamento > Importar eSocial**.
*   **Opção A (Drag & Drop):** Arraste o arquivo XML (Evento S-5002 ou lote) para a área indicada.
*   **Opção B (Seleção):** Clique para selecionar o arquivo no seu computador.
*   O sistema realizará:
    1.  Validação de Schema (XSD).
    2.  Verificação de integridade de CPFs.
    3.  Preview dos dados extraídos.
*   Clique em **Confirmar e Processar**.
*   Acompanhe o status em **Jobs de Processamento** (Pendente -> Processando -> Concluído/Erro).

### 5. Geração de Comprovantes (PDF)
*   Após o processamento bem-sucedido, vá para **Funcionários** ou **Rendimentos**.
*   Utilize os filtros para encontrar o período ou colaborador desejado.
*   **Individual:** Clique no ícone de PDF ao lado do nome do funcionário.
*   **Em Lote:** Selecione múltiplos funcionários (checkbox) e clique em **Gerar Comprovantes Selecionados**.
*   O sistema gerará um arquivo ZIP contendo todos os PDFs nominados corretamente.

### 6. Integrações e API para Parceiros (Fase 6)
*   Acesse **Desenvolvedores > API Keys** no menu de Administração.
*   Clique em **Gerar Nova Chave**. Dê um nome descritivo (ex: "Integração ERP Interno").
*   Copie a chave imediatamente (ela não será mostrada novamente).
*   Use a documentação interativa em `https://api.suaempresa.com/docs` para testar endpoints.
*   **Webhooks:** Em **Desenvolvedores > Webhooks**, cadastre a URL do seu sistema para receber eventos como `pdf.generated`, `xml.processed`, `billing.invoice_paid`.

---

## 6. 🆘 Suporte e Monitoramento

Ferramentas para operações (DevOps) e troubleshooting.

### Logs em Tempo Real
```bash
# Logs da API
kubectl logs -f deployment/api-esocial -n esocial-prod

# Logs do Frontend
kubectl logs -f deployment/web-esocial -n esocial-prod

# Filtrar por erro
kubectl logs -f deployment/api-esocial -n esocial-prod | grep "ERROR"
```

### Métricas e Dashboards
*   **Prometheus/Grafana:** Acesse `http://grafana.seu-domínio.com`.
    *   Login: `admin` / Senha: (definida no secret).
    *   Dashboards pré-configurados: "API Latency", "Error Rates", "Pod CPU/Memory", "Business Metrics (PDFs gerados/hora)".
*   **Alertas:** Configurados para disparar no Slack/PagerDuty se:
    *   Error Rate > 1% por 5 minutos.
    *   Latência P95 > 2 segundos.
    *   Pods reiniciando constantemente (CrashLoopBackOff).

### Rastreabilidade Distribuída (Tracing)
*   **Jaeger:** Acesse `http://jaeger.seu-domínio.com`.
    *   Útil para investigar lentidão em requisições específicas.
    *   Busque por Trace ID retornado nos headers da resposta (`X-Trace-ID`).

### Backup e Recuperação de Desastres (DR)
*   **Backup Automático:** Configurado via CronJob no Kubernetes (`k8s/cronjob-backup.yaml`) rodando diariamente às 03:00 UTC.
*   **Restauração:**
    ```bash
    # Restaurar backup mais recente
    kubectl job create restore-job --from=cronjob/backup-db -n esocial-prod
    # (Ajuste o script do job para apontar para o arquivo de backup específico no S3/GCS)
    ```

---

## 7. 🔧 Solução de Problemas Comuns

| Problema | Causa Provável | Solução |
| :--- | :--- | :--- |
| **Erro 500 ao fazer upload** | Tamanho do arquivo excede limite | Aumente `client_max_body_size` no Ingress/Nginx ou verifique `MAX_UPLOAD_SIZE` no .env. |
| **PDF não gera** | Fonte faltando no container | Verifique se o pacote de fontes está instalado no `Dockerfile.web` ou `api`. |
| **Webhook Stripe falha** | Secret incorreto ou URL inacessível | Verifique `STRIPE_WEBHOOK_SECRET` e se a URL está acessível publicamente (não use localhost em prod). |
| **Login falha (401)** | JWT Secret divergente | Garanta que `JWT_SECRET` é idêntico no backend e nas variáveis de ambiente do pod. |
| **Banco de dados lento** | Falta de índices | Execute `alembic upgrade head` para garantir migrations recentes ou analise queries lentas no PGLogs. |
| **Pods em CrashLoopBackOff** | Erro de configuração/env | Execute `kubectl describe pod <nome-do-pod>` e verifique a seção "Events" e "Logs". |

---

## 🎉 Parabéns!

Você agora possui um **SaaS Enterprise de Comprovantes de Rendimentos** completo, escalável, seguro e pronto para competir no mercado.

**Resumo do que foi entregue:**
*   ✅ **Multi-Tenant:** Isolamento total de dados por empresa.
*   ✅ **Segurança:** RBAC, Audit Logs, Criptografia, MFA pronto.
*   ✅ **Escalabilidade:** Arquitetura stateless pronta para K8s e Auto-scaling.
*   ✅ **Financeiro:** Integração completa com Stripe para assinaturas recorrentes.
*   ✅ **UX Premium:** Frontend Next.js moderno e responsivo.
*   ✅ **Ecossistema:** API Pública, Webhooks e SDKs prontos para integrações.

**Próximos passos sugeridos para o Time de Produto:**
1.  Contratar domínio e configurar SSL (Let's Encrypt ou Comercial).
2.  Configurar SMTP real (SendGrid/AWS SES) para entrega de e-mails transacionais.
3.  Cadastrar primeiros clientes Beta e coletar feedback.
4.  Implementar campanhas de Marketing para lançamento oficial.

---
*Documento gerado automaticamente como parte da Fase 6: Ecosystem.*
