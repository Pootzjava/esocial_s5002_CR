# eSocial Rendimentos SaaS - Developer Portal

Bem-vindo ao **Developer Portal** do eSocial Rendimentos SaaS. Aqui você encontrará toda a documentação necessária para integrar seu sistema com nossa API pública.

## 📚 Índice

1. [Visão Geral](#visão-geral)
2. [Autenticação](#autenticação)
3. [Endpoints da API](#endpoints-da-api)
4. [Webhooks](#webhooks)
5. [SDKs e Exemplos](#sdks-e-exemplos)
6. [Rate Limits](#rate-limits)
7. [Versionamento](#versionamento)
8. [Suporte](#suporte)

---

## Visão Geral

A API do eSocial Rendimentos SaaS permite que você integre funcionalidades de emissão de comprovantes de rendimentos diretamente em seu sistema. 

**Base URL:** `https://api.esocialrendimentos.com.br`

**Versão atual:** `v1`

### Recursos Principais

- ✅ Gestão de funcionários
- ✅ Consulta de eventos de rendimento (eSocial S-5002)
- ✅ Geração de PDFs de comprovantes
- ✅ Webhooks para eventos em tempo real
- ✅ Multi-tenancy com isolamento de dados

---

## Autenticação

Todas as requisições à API devem incluir uma **API Key** válida no header:

```http
X-API-Key: esr_sua_api_key_aqui
```

### Como Obter uma API Key

1. Acesse o dashboard em `https://app.esocialrendimentos.com.br`
2. Navegue até **Configurações > API Keys**
3. Clique em **"Criar Nova API Key"**
4. Selecione as permissões desejadas
5. Copie e guarde sua chave (ela só será mostrada uma vez)

### Permissões Disponíveis

| Permissão | Descrição |
|-----------|-----------|
| `read:employees` | Ler lista de funcionários |
| `read:events` | Ler eventos de rendimento |
| `write:pdf` | Gerar e baixar PDFs |
| `manage:webhooks` | Criar e gerenciar webhooks |

---

## Endpoints da API

### Funcionários

#### `GET /api/v1/employees`
Lista funcionários da empresa.

**Parâmetros Query:**
- `limit` (int, opcional): Número máximo de registros (padrão: 50)
- `offset` (int, opcional): Offset para paginação (padrão: 0)
- `search` (string, opcional): Busca por nome ou CPF

**Exemplo:**
```bash
curl -X GET "https://api.esocialrendimentos.com.br/api/v1/employees?limit=10&search=Joao" \
  -H "X-API-Key: esr_sua_key"
```

**Resposta:**
```json
{
  "employees": [
    {
      "id": "emp_12345",
      "name": "João Silva",
      "cpf": "123.456.789-00",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 1,
  "limit": 10,
  "offset": 0
}
```

#### `GET /api/v1/employees/{employee_id}`
Obtém detalhes de um funcionário específico.

---

### Eventos de Rendimento

#### `GET /api/v1/income-events`
Lista eventos de rendimento.

**Parâmetros Query:**
- `employee_id` (string, opcional): Filtrar por funcionário
- `year` (int, opcional): Filtrar por ano
- `month` (int, opcional): Filtrar por mês
- `limit` (int, opcional): Número máximo de registros

**Exemplo:**
```bash
curl -X GET "https://api.esocialrendimentos.com.br/api/v1/income-events?year=2024&month=1" \
  -H "X-API-Key: esr_sua_key"
```

---

### PDF

#### `POST /api/v1/pdf/generate`
Gera comprovantes de rendimentos em PDF.

**Body:**
```json
{
  "employee_ids": ["emp_12345", "emp_67890"],
  "template_id": "default"
}
```

**Resposta:**
```json
{
  "job_id": "job_abc123",
  "status": "processing",
  "created_at": "2024-01-20T14:30:00Z",
  "estimated_completion": "2024-01-20T14:32:00Z"
}
```

#### `GET /api/v1/pdf/status/{job_id}`
Verifica status do job de geração.

#### `GET /api/v1/pdf/download/{pdf_id}`
Baixa o PDF gerado.

---

### Webhooks

#### `POST /api/v1/webhooks`
Cria um webhook para receber notificações.

**Body:**
```json
{
  "url": "https://meu-sistema.com.br/webhooks/esocial",
  "events": ["employee.created", "pdf.generated"],
  "secret": "meu_secret_super_seguro"
}
```

**Eventos Disponíveis:**
- `employee.created` - Novo funcionário cadastrado
- `employee.updated` - Funcionário atualizado
- `income_event.created` - Novo evento de rendimento
- `pdf.generated` - PDF gerado com sucesso
- `pdf.failed` - Falha na geração do PDF
- `processing.completed` - Processamento em lote concluído

---

## Webhooks

### Recebendo Webhooks

Quando um evento ocorre, enviamos uma requisição POST para sua URL configurada:

**Headers:**
```http
Content-Type: application/json
X-Webhook-ID: wh_abc123
X-Webhook-Signature: sha256=abcdef123456...
X-Webhook-Timestamp: 1705762800
```

**Body:**
```json
{
  "id": "wh_abc123",
  "type": "pdf.generated",
  "timestamp": "2024-01-20T14:32:00Z",
  "data": {
    "pdf_id": "pdf_xyz789",
    "employee_id": "emp_12345",
    "file_url": "https://storage.../pdf_xyz789.pdf"
  }
}
```

### Validando Assinatura

Sempre valide a assinatura HMAC-SHA256 para garantir autenticidade:

**Python:**
```python
import hmac
import hashlib

def verify_signature(payload, signature, secret):
    expected = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    received = signature.replace('sha256=', '')
    return hmac.compare_digest(expected, received)
```

**Node.js:**
```javascript
const crypto = require('crypto');

function verifySignature(payload, signature, secret) {
    const expected = crypto
        .createHmac('sha256', secret)
        .update(payload)
        .digest('hex');
    
    const received = signature.replace('sha256=', '');
    return crypto.timingSafeEqual(
        Buffer.from(expected),
        Buffer.from(received)
    );
}
```

---

## SDKs e Exemplos

### Python SDK

**Instalação:**
```bash
pip install requests
```

**Uso:**
```python
from examples.python.example import ESocialRendimentosClient

client = ESocialRendimentosClient(api_key="esr_sua_key")

# Listar funcionários
employees = client.list_employees(limit=10)

# Gerar PDF
job = client.generate_pdf(employee_ids=["emp_12345"])
```

📁 Exemplo completo: [`sdk-examples/python/example.py`](../sdk-examples/python/example.py)

### Node.js SDK

**Instalação:**
```bash
npm install axios dotenv
```

**Uso:**
```javascript
const ESocialRendimentosClient = require('./examples/nodejs/example');

const client = new ESocialRendimentosClient('esr_sua_key');

// Listar funcionários
const employees = await client.listEmployees(10);

// Gerar PDF
const job = await client.generatePdf(['emp_12345']);
```

📁 Exemplo completo: [`sdk-examples/nodejs/example.js`](../sdk-examples/nodejs/example.js)

### cURL Examples

📁 Veja exemplos cURL em: `docs/developer-portal/curl-examples.md`

---

## Rate Limits

| Plano | Limite | Requests/Hora |
|-------|--------|---------------|
| Free | Básico | 100 |
| Starter | Profissional | 1,000 |
| Business | Empresarial | 5,000 |
| Enterprise | Corporativo | 10,000+ |

### Headers de Rate Limit

Cada resposta inclui headers informando seu uso atual:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 847
X-RateLimit-Reset: 1705766400
```

### Boas Práticas

- Implemente retry com backoff exponencial
- Cache respostas quando possível
- Use webhooks em vez de polling
- Agrupe requisições quando aplicável

---

## Versionamento

A API usa versionamento via URL: `/api/v1/`, `/api/v2/`, etc.

- **Versões ativas:** v1
- **Versões depreciadas:** Nenhuma
- **Política:** Versões são suportadas por mínimo de 12 meses após anúncio de depreciação

### Changelog

**v1.0.0** (Janeiro 2024)
- Lançamento inicial da API pública
- Suporte a funcionários, eventos, PDFs e webhooks
- SDKs Python e Node.js

---

## Suporte

### Canais de Atendimento

- 📧 Email: `developers@esocialrendimentos.com.br`
- 💬 Slack: [Comunidade de Desenvolvedores](https://slack.esocialrendimentos.com.br)
- 📖 Documentação: https://docs.esocialrendimentos.com.br
- 🐛 Issues: https://github.com/esocial-rendimentos/api-issues

### Status da API

Verifique o status atual em: https://status.esocialrendimentos.com.br

---

## Termos de Uso

Ao usar esta API, você concorda com nossos [Termos de Serviço](https://esocialrendimentos.com.br/terms) e [Política de Privacidade](https://esocialrendimentos.com.br/privacy).

**Proibido:**
- Reverse engineering da API
- Compartilhamento de API Keys
- Uso para fins ilegais ou não autorizados
- Exceder rate limits intencionalmente

---

© 2024 eSocial Rendimentos SaaS. Todos os direitos reservados.
