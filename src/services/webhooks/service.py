"""
eSocial Rendimentos SaaS - Webhook Service
Fase 6: Ecosystem - Serviço de Disparo e Gestão de Webhooks
"""

import aiohttp
import hashlib
import hmac
import json
from datetime import datetime
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class WebhookService:
    """Serviço responsável por disparar webhooks para endpoints externos."""
    
    def __init__(self):
        self.timeout = aiohttp.ClientTimeout(total=30)
        self.max_retries = 3
        self.retry_delay = 5  # segundos
    
    async def send_webhook(
        self,
        url: str,
        event_type: str,
        payload: Dict[str, Any],
        secret: str,
        webhook_id: str
    ) -> bool:
        """
        Envia um webhook para um endpoint externo com assinatura HMAC.
        
        Args:
            url: URL do endpoint destino
            event_type: Tipo do evento (ex: employee.created)
            payload: Dados do evento em formato dict
            secret: Secret para assinatura HMAC
            webhook_id: ID do webhook configurado
            
        Returns:
            bool: True se enviado com sucesso, False caso contrário
        """
        headers = {
            'Content-Type': 'application/json',
            'X-Webhook-ID': webhook_id,
            'X-Webhook-Signature': self._generate_signature(payload, secret),
            'X-Webhook-Timestamp': str(int(datetime.utcnow().timestamp())),
            'User-Agent': 'eSocial-Rendimentos-Webhook/1.0'
        }
        
        body = json.dumps({
            'id': webhook_id,
            'type': event_type,
            'timestamp': datetime.utcnow().isoformat(),
            'data': payload
        })
        
        for attempt in range(self.max_retries):
            try:
                async with aiohttp.ClientSession(timeout=self.timeout) as session:
                    async with session.post(url, data=body, headers=headers) as response:
                        if response.status == 200:
                            logger.info(f"Webhook {webhook_id} enviado com sucesso para {url}")
                            return True
                        else:
                            logger.warning(f"Webhook {webhook_id} falhou com status {response.status}")
                            
            except aiohttp.ClientError as e:
                logger.error(f"Erro ao enviar webhook {webhook_id}: {str(e)}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                continue
        
        logger.error(f"Webhook {webhook_id} falhou após {self.max_retries} tentativas")
        return False
    
    def _generate_signature(self, payload: Dict[str, Any], secret: str) -> str:
        """Gera assinatura HMAC-SHA256 para validar a autenticidade do webhook."""
        payload_str = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            secret.encode('utf-8'),
            payload_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return f"sha256={signature}"
    
    @staticmethod
    def verify_signature(payload: str, signature: str, secret: str) -> bool:
        """
        Verifica a assinatura de um webhook recebido.
        Útil para validar webhooks de provedores externos (ex: Stripe).
        
        Args:
            payload: String JSON do payload recebido
            signature: Assinatura recebida no header
            secret: Secret compartilhado
            
        Returns:
            bool: True se assinatura válida, False caso contrário
        """
        if not signature.startswith('sha256='):
            return False
        
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        received_signature = signature.replace('sha256=', '')
        
        return hmac.compare_digest(expected_signature, received_signature)


# Eventos disponíveis para webhooks
WEBHOOK_EVENTS = [
    "employee.created",
    "employee.updated",
    "employee.deleted",
    "income_event.created",
    "income_event.updated",
    "pdf.generated",
    "pdf.failed",
    "processing.started",
    "processing.completed",
    "processing.failed",
    "billing.subscription_created",
    "billing.subscription_updated",
    "billing.subscription_deleted",
    "billing.payment_succeeded",
    "billing.payment_failed"
]


async def trigger_webhook_event(
    event_type: str,
    data: Dict[str, Any],
    tenant_id: str,
    webhooks_config: List[Dict[str, Any]]
):
    """
    Dispara um evento de webhook para todos os webhooks configurados que escutam este tipo de evento.
    
    Args:
        event_type: Tipo do evento (deve estar em WEBHOOK_EVENTS)
        data: Dados do evento
        tenant_id: ID do tenant proprietário do evento
        webhooks_config: Lista de configurações de webhooks do tenant
    """
    if event_type not in WEBHOOK_EVENTS:
        logger.warning(f"Tentativa de disparar evento desconhecido: {event_type}")
        return
    
    service = WebhookService()
    
    for webhook in webhooks_config:
        if not webhook.get('active', True):
            continue
            
        if event_type not in webhook.get('events', []):
            continue
        
        payload = {
            'tenant_id': tenant_id,
            'event_type': event_type,
            'data': data
        }
        
        success = await service.send_webhook(
            url=webhook['url'],
            event_type=event_type,
            payload=payload,
            secret=webhook['secret'],
            webhook_id=webhook['id']
        )
        
        # Atualizar estatísticas do webhook (em produção, salvar no DB)
        if success:
            webhook['success_count'] = webhook.get('success_count', 0) + 1
            webhook['last_triggered'] = datetime.utcnow()
        else:
            webhook['failure_count'] = webhook.get('failure_count', 0) + 1


# Exemplo de uso em outros módulos
async def notify_employee_created(employee_data: dict, tenant_id: str, webhooks: list):
    """Notifica webhooks quando um funcionário é criado."""
    await trigger_webhook_event(
        event_type="employee.created",
        data=employee_data,
        tenant_id=tenant_id,
        webhooks_config=webhooks
    )


async def notify_pdf_generated(pdf_data: dict, tenant_id: str, webhooks: list):
    """Notifica webhooks quando um PDF é gerado."""
    await trigger_webhook_event(
        event_type="pdf.generated",
        data=pdf_data,
        tenant_id=tenant_id,
        webhooks_config=webhooks
    )
