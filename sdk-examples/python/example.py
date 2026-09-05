"""
eSocial Rendimentos SaaS - Python SDK Example
Fase 6: Ecosystem - Exemplo de uso do SDK Python para integração

Instalação:
    pip install requests python-dotenv

Uso:
    export ESOCIAL_API_KEY="sua_api_key_aqui"
    python example.py
"""

import os
import requests
from typing import List, Optional, Dict, Any
from datetime import datetime


class ESocialRendimentosClient:
    """Cliente Python para integração com a API do eSocial Rendimentos SaaS."""
    
    def __init__(self, api_key: str, base_url: str = "https://api.esocialrendimentos.com.br"):
        """
        Inicializa o cliente com API Key e URL base.
        
        Args:
            api_key: Sua API Key obtida no dashboard
            base_url: URL base da API (padrão: produção)
        """
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-Key': api_key,
            'Content-Type': 'application/json',
            'User-Agent': 'eSocial-Rendimentos-Python-SDK/1.0.0'
        })
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Realiza uma requisição HTTP com tratamento de erros."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP Error {e.response.status_code}: {e.response.text}"
            raise Exception(error_msg)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
    
    # Funcionalidades de Funcionários
    def list_employees(self, limit: int = 50, offset: int = 0, search: Optional[str] = None) -> List[Dict]:
        """
        Lista funcionários da empresa.
        
        Args:
            limit: Número máximo de registros (padrão: 50)
            offset: Offset para paginação (padrão: 0)
            search: Termo de busca opcional (nome ou CPF)
            
        Returns:
            Lista de dicionários com dados dos funcionários
        """
        params = {'limit': limit, 'offset': offset}
        if search:
            params['search'] = search
        
        result = self._request('GET', '/api/v1/employees', params=params)
        return result.get('employees', [])
    
    def get_employee(self, employee_id: str) -> Dict:
        """
        Obtém detalhes de um funcionário específico.
        
        Args:
            employee_id: ID do funcionário
            
        Returns:
            Dicionário com dados completos do funcionário
        """
        return self._request('GET', f'/api/v1/employees/{employee_id}')
    
    # Funcionalidades de Eventos de Rendimento
    def list_income_events(
        self, 
        employee_id: Optional[str] = None,
        year: Optional[int] = None,
        month: Optional[int] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Lista eventos de rendimento.
        
        Args:
            employee_id: Filtrar por funcionário específico
            year: Filtrar por ano
            month: Filtrar por mês
            limit: Número máximo de registros
            
        Returns:
            Lista de eventos de rendimento
        """
        params = {'limit': limit}
        if employee_id:
            params['employee_id'] = employee_id
        if year:
            params['year'] = year
        if month:
            params['month'] = month
        
        result = self._request('GET', '/api/v1/income-events', params=params)
        return result.get('events', [])
    
    # Funcionalidades de PDF
    def generate_pdf(self, employee_ids: List[str], template_id: str = "default") -> Dict:
        """
        Gera comprovantes de rendimentos em PDF.
        
        Args:
            employee_ids: Lista de IDs de funcionários para gerar PDF
            template_id: ID do template a ser usado (padrão: "default")
            
        Returns:
            Dicionário com informações do job de geração
        """
        payload = {
            'employee_ids': employee_ids,
            'template_id': template_id
        }
        return self._request('POST', '/api/v1/pdf/generate', json=payload)
    
    def get_pdf_status(self, job_id: str) -> Dict:
        """
        Verifica status de um job de geração de PDF.
        
        Args:
            job_id: ID do job de geração
            
        Returns:
            Status atual do job
        """
        return self._request('GET', f'/api/v1/pdf/status/{job_id}')
    
    def download_pdf(self, pdf_id: str, save_path: str) -> str:
        """
        Baixa um PDF gerado e salva em arquivo local.
        
        Args:
            pdf_id: ID do PDF gerado
            save_path: Caminho completo para salvar o arquivo
            
        Returns:
            Caminho do arquivo salvo
        """
        response = self._request('GET', f'/api/v1/pdf/download/{pdf_id}')
        
        # Em produção, isso seria um stream de bytes
        # Aqui estamos simulando
        with open(save_path, 'wb') as f:
            f.write(b'Simulated PDF content')  # Substituir pelo conteúdo real
        
        return save_path
    
    # Funcionalidades de Webhooks
    def create_webhook(self, url: str, events: List[str], secret: Optional[str] = None) -> Dict:
        """
        Cria um webhook para receber notificações de eventos.
        
        Args:
            url: URL do endpoint que receberá os webhooks
            events: Lista de tipos de evento para subscrição
            secret: Secret opcional para assinatura HMAC
            
        Returns:
            Informações do webhook criado
        """
        payload = {
            'url': url,
            'events': events,
            'secret': secret
        }
        return self._request('POST', '/api/v1/webhooks', json=payload)
    
    def list_webhooks(self) -> List[Dict]:
        """Lista todos os webhooks configurados."""
        result = self._request('GET', '/api/v1/webhooks')
        return result.get('webhooks', [])
    
    def delete_webhook(self, webhook_id: str) -> Dict:
        """Remove um webhook configurado."""
        return self._request('DELETE', f'/api/v1/webhooks/{webhook_id}')
    
    # Utilitários
    def get_rate_limit(self) -> Dict:
        """Verifica limites de uso da API."""
        return self._request('GET', '/api/v1/rate-limit')
    
    def health_check(self) -> Dict:
        """Verifica saúde da API."""
        return self._request('GET', '/api/v1/health')


# Exemplo de uso
if __name__ == "__main__":
    # Configurar API Key (em produção, usar variáveis de ambiente)
    API_KEY = os.getenv("ESOCIAL_API_KEY", "esr_demo_key_12345")
    
    # Inicializar cliente
    client = ESocialRendimentosClient(api_key=API_KEY)
    
    print("=" * 60)
    print("eSocial Rendimentos SaaS - Python SDK Example")
    print("=" * 60)
    
    try:
        # 1. Health Check
        print("\n1. Verificando saúde da API...")
        health = client.health_check()
        print(f"   Status: {health.get('status')}")
        print(f"   Versão: {health.get('version')}")
        
        # 2. Listar funcionários
        print("\n2. Listando funcionários...")
        employees = client.list_employees(limit=10)
        print(f"   Encontrados {len(employees)} funcionários")
        for emp in employees[:3]:  # Mostrar apenas 3
            print(f"   - {emp.get('name', 'N/A')} (CPF: {emp.get('cpf', 'N/A')})")
        
        # 3. Listar eventos de rendimento
        print("\n3. Listando eventos de rendimento...")
        events = client.list_income_events(year=2024, limit=5)
        print(f"   Encontrados {len(events)} eventos")
        
        # 4. Gerar PDF
        print("\n4. Gerando comprovante de rendimentos em PDF...")
        if employees:
            employee_id = employees[0].get('id')
            job = client.generate_pdf(employee_ids=[employee_id])
            print(f"   Job ID: {job.get('job_id')}")
            print(f"   Status: {job.get('status')}")
        
        # 5. Criar webhook
        print("\n5. Configurando webhook...")
        webhook = client.create_webhook(
            url="https://meu-sistema.com.br/webhooks/esocial",
            events=["employee.created", "pdf.generated"],
            secret="meu_secret_super_seguro"
        )
        print(f"   Webhook ID: {webhook.get('webhook_id')}")
        print(f"   URL: {webhook.get('url')}")
        print(f"   Eventos: {', '.join(webhook.get('events', []))}")
        
        # 6. Verificar rate limit
        print("\n6. Verificando limite de uso da API...")
        rate_limit = client.get_rate_limit()
        print(f"   Limite: {rate_limit.get('limit')} requests/hora")
        print(f"   Restante: {rate_limit.get('remaining')} requests")
        
        print("\n" + "=" * 60)
        print("Exemplo concluído com sucesso!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")
        print("\nDica: Certifique-se de que a API_KEY está configurada corretamente.")
