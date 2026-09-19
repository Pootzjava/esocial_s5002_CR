/**
 * eSocial Rendimentos SaaS - Node.js SDK Example
 * Fase 6: Ecosystem - Exemplo de uso do SDK JavaScript/Node.js para integração
 * 
 * Instalação:
 *   npm install axios dotenv
 * 
 * Uso:
 *   export ESOCIAL_API_KEY="sua_api_key_aqui"
 *   node example.js
 */

const axios = require('axios');
require('dotenv').config();

class ESocialRendimentosClient {
    /**
     * Inicializa o cliente com API Key e URL base.
     * @param {string} apiKey - Sua API Key obtida no dashboard
     * @param {string} baseUrl - URL base da API (padrão: produção)
     */
    constructor(apiKey, baseUrl = 'https://api.esocialrendimentos.com.br') {
        this.apiKey = apiKey;
        this.baseUrl = baseUrl;
        
        this.client = axios.create({
            baseURL: baseUrl,
            headers: {
                'X-API-Key': apiKey,
                'Content-Type': 'application/json',
                'User-Agent': 'eSocial-Rendimentos-NodeJS-SDK/1.0.0'
            }
        });
        
        // Interceptor para tratamento de erros
        this.client.interceptors.response.use(
            response => response,
            error => {
                const message = error.response?.data?.detail || error.message;
                throw new Error(`API Error: ${message}`);
            }
        );
    }

    /**
     * Lista funcionários da empresa.
     * @param {number} limit - Número máximo de registros (padrão: 50)
     * @param {number} offset - Offset para paginação (padrão: 0)
     * @param {string} search - Termo de busca opcional
     * @returns {Promise<Array>} Lista de funcionários
     */
    async listEmployees(limit = 50, offset = 0, search = null) {
        const params = { limit, offset };
        if (search) params.search = search;
        
        const response = await this.client.get('/api/v1/employees', { params });
        return response.data.employees || [];
    }

    /**
     * Obtém detalhes de um funcionário específico.
     * @param {string} employeeId - ID do funcionário
     * @returns {Promise<Object>} Dados completos do funcionário
     */
    async getEmployee(employeeId) {
        const response = await this.client.get(`/api/v1/employees/${employeeId}`);
        return response.data;
    }

    /**
     * Lista eventos de rendimento.
     * @param {Object} filters - Filtros opcionais
     * @param {string} filters.employeeId - Filtrar por funcionário
     * @param {number} filters.year - Filtrar por ano
     * @param {number} filters.month - Filtrar por mês
     * @param {number} filters.limit - Número máximo de registros
     * @returns {Promise<Array>} Lista de eventos de rendimento
     */
    async listIncomeEvents({ employeeId, year, month, limit = 100 } = {}) {
        const params = { limit };
        if (employeeId) params.employee_id = employeeId;
        if (year) params.year = year;
        if (month) params.month = month;
        
        const response = await this.client.get('/api/v1/income-events', { params });
        return response.data.events || [];
    }

    /**
     * Gera comprovantes de rendimentos em PDF.
     * @param {Array<string>} employeeIds - Lista de IDs de funcionários
     * @param {string} templateId - ID do template (padrão: "default")
     * @returns {Promise<Object>} Informações do job de geração
     */
    async generatePdf(employeeIds, templateId = 'default') {
        const response = await this.client.post('/api/v1/pdf/generate', {
            employee_ids: employeeIds,
            template_id: templateId
        });
        return response.data;
    }

    /**
     * Verifica status de um job de geração de PDF.
     * @param {string} jobId - ID do job de geração
     * @returns {Promise<Object>} Status atual do job
     */
    async getPdfStatus(jobId) {
        const response = await this.client.get(`/api/v1/pdf/status/${jobId}`);
        return response.data;
    }

    /**
     * Cria um webhook para receber notificações de eventos.
     * @param {string} url - URL do endpoint que receberá os webhooks
     * @param {Array<string>} events - Lista de tipos de evento
     * @param {string} secret - Secret opcional para assinatura HMAC
     * @returns {Promise<Object>} Informações do webhook criado
     */
    async createWebhook(url, events, secret = null) {
        const response = await this.client.post('/api/v1/webhooks', {
            url,
            events,
            secret
        });
        return response.data;
    }

    /**
     * Lista todos os webhooks configurados.
     * @returns {Promise<Array>} Lista de webhooks
     */
    async listWebhooks() {
        const response = await this.client.get('/api/v1/webhooks');
        return response.data.webhooks || [];
    }

    /**
     * Remove um webhook configurado.
     * @param {string} webhookId - ID do webhook
     * @returns {Promise<Object>} Confirmação de remoção
     */
    async deleteWebhook(webhookId) {
        const response = await this.client.delete(`/api/v1/webhooks/${webhookId}`);
        return response.data;
    }

    /**
     * Verifica limites de uso da API.
     * @returns {Promise<Object>} Informações de rate limit
     */
    async getRateLimit() {
        const response = await this.client.get('/api/v1/rate-limit');
        return response.data;
    }

    /**
     * Verifica saúde da API.
     * @returns {Promise<Object>} Status da API
     */
    async healthCheck() {
        const response = await this.client.get('/api/v1/health');
        return response.data;
    }
}

// Exemplo de uso
async function main() {
    console.log('='.repeat(60));
    console.log('eSocial Rendimentos SaaS - Node.js SDK Example');
    console.log('='.repeat(60));

    const API_KEY = process.env.ESOCIAL_API_KEY || 'esr_demo_key_12345';
    const client = new ESocialRendimentosClient(API_KEY);

    try {
        // 1. Health Check
        console.log('\n1. Verificando saúde da API...');
        const health = await client.healthCheck();
        console.log(`   Status: ${health.status}`);
        console.log(`   Versão: ${health.version}`);

        // 2. Listar funcionários
        console.log('\n2. Listando funcionários...');
        const employees = await client.listEmployees(10);
        console.log(`   Encontrados ${employees.length} funcionários`);
        employees.slice(0, 3).forEach(emp => {
            console.log(`   - ${emp.name} (CPF: ${emp.cpf})`);
        });

        // 3. Listar eventos de rendimento
        console.log('\n3. Listando eventos de rendimento...');
        const events = await client.listIncomeEvents({ year: 2024, limit: 5 });
        console.log(`   Encontrados ${events.length} eventos`);

        // 4. Gerar PDF
        console.log('\n4. Gerando comprovante de rendimentos em PDF...');
        if (employees.length > 0) {
            const job = await client.generatePdf([employees[0].id]);
            console.log(`   Job ID: ${job.job_id}`);
            console.log(`   Status: ${job.status}`);
        }

        // 5. Criar webhook
        console.log('\n5. Configurando webhook...');
        const webhook = await client.createWebhook(
            'https://meu-sistema.com.br/webhooks/esocial',
            ['employee.created', 'pdf.generated'],
            'meu_secret_super_seguro'
        );
        console.log(`   Webhook ID: ${webhook.webhook_id}`);
        console.log(`   URL: ${webhook.url}`);
        console.log(`   Eventos: ${webhook.events.join(', ')}`);

        // 6. Verificar rate limit
        console.log('\n6. Verificando limite de uso da API...');
        const rateLimit = await client.getRateLimit();
        console.log(`   Limite: ${rateLimit.limit} requests/hora`);
        console.log(`   Restante: ${rateLimit.remaining} requests`);

        console.log('\n' + '='.repeat(60));
        console.log('Exemplo concluído com sucesso!');
        console.log('='.repeat(60));

    } catch (error) {
        console.error(`\n❌ Erro: ${error.message}`);
        console.error('\nDica: Certifique-se de que a API_KEY está configurada corretamente.');
    }
}

// Executar exemplo
main();

module.exports = ESocialRendimentosClient;
