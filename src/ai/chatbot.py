"""
Chatbot inteligente para suporte ao usuário do eSocial Rendimentos.
Responde dúvidas sobre legislação, prazos e funcionalidades do sistema.
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ChatMessage:
    """Mensagem do chat."""
    role: str  # user, assistant, system
    content: str
    timestamp: datetime
    metadata: Optional[Dict] = None


@dataclass
class ChatResponse:
    """Resposta do chatbot."""
    message: str
    confidence: float
    suggested_actions: List[str]
    sources: List[str]
    conversation_id: str


class KnowledgeBase:
    """Base de conhecimento sobre eSocial e legislação trabalhista."""
    
    def __init__(self):
        self.topics = {
            'prazo_esocial': {
                'keywords': ['prazo', 'deadline', 'data limite', 'quando enviar'],
                'response': (
                    "Os prazos do eSocial variam conforme o evento:\n"
                    "• S-5002 (Rendimentos): Até o dia 15 do mês subsequente\n"
                    "• S-5003 (Comprovante): Geração imediata após processamento\n"
                    "• DIRF: Normalmente até o último dia útil de fevereiro\n\n"
                    "Recomendo sempre verificar o calendário oficial da Receita Federal."
                ),
                'sources': ['Instrução Normativa RFB nº 2.099/2022']
            },
            'comprovante_rendimentos': {
                'keywords': ['comprovante', 'informe', 'rendimentos', 'entregar'],
                'response': (
                    "O Comprovante de Rendimentos é obrigatório e deve ser entregue:\n"
                    "1. Para empregados: Até 15/02 do ano seguinte\n"
                    "2. Formato: PDF assinado digitalmente ou via eSocial\n"
                    "3. Conteúdo: Rendimentos totais, descontos de IRRF, contribuições\n\n"
                    "Nosso sistema gera automaticamente este documento a partir dos eventos S-5002."
                ),
                'sources': ['Lei 7.713/88', 'IN RFB 2.099/2022']
            },
            'multas_atraso': {
                'keywords': ['multa', 'atraso', 'penalidade', 'sanção'],
                'response': (
                    "As multas por atraso no eSocial podem variar:\n"
                    "• Por evento não enviado: R$ 400,00 a R$ 3.000,00\n"
                    "• Limite mensal: 8% da folha de pagamento\n"
                    "• Reincidência: Valores podem dobrar\n\n"
                    "Nosso sistema envia alertas automáticos antes dos prazos!"
                ),
                'sources': ['Art. 32-A da Lei 8.218/91']
            },
            'como_usar_sistema': {
                'keywords': ['como usar', 'tutorial', 'ajuda', 'funcionalidade'],
                'response': (
                    "Para usar nosso sistema:\n"
                    "1. Faça login com suas credenciais\n"
                    "2. Vá em 'Upload XML' e envie os arquivos do eSocial\n"
                    "3. O sistema valida automaticamente os dados\n"
                    "4. Gere os comprovantes em PDF com um clique\n"
                    "5. Envie por email ou disponibilize no portal do funcionário\n\n"
                    "Precisa de ajuda específica? Me pergunte sobre qualquer etapa!"
                ),
                'sources': ['Manual do Usuário v2.0']
            },
            'seguranca_dados': {
                'keywords': ['segurança', 'lgpd', 'proteção', 'dados pessoais'],
                'response': (
                    "Seus dados estão protegidos com:\n"
                    "• Criptografia AES-256 em repouso e TLS 1.3 em trânsito\n"
                    "• Conformidade total com LGPD (Lei 13.709/2018)\n"
                    "• Backups diários em múltiplas regiões\n"
                    "• Auditoria completa de todos os acessos\n"
                    "• Certificações SOC 2 Type II e ISO 27001\n\n"
                    "Seus dados são seus - nunca compartilhamos com terceiros."
                ),
                'sources': ['Política de Privacidade', 'LGPD']
            }
        }
    
    def search(self, query: str) -> List[Dict]:
        """Busca tópicos relevantes na base de conhecimento."""
        query_lower = query.lower()
        results = []
        
        for topic_id, topic_data in self.topics.items():
            # Verifica se alguma keyword está na query
            for keyword in topic_data['keywords']:
                if keyword in query_lower:
                    results.append({
                        'topic_id': topic_id,
                        'response': topic_data['response'],
                        'sources': topic_data['sources'],
                        'relevance_score': 0.9  # Score fixo para demo
                    })
                    break
        
        return results


class ChatbotService:
    """Serviço de chatbot com IA para suporte."""
    
    def __init__(self):
        self.knowledge_base = KnowledgeBase()
        self.conversations: Dict[str, List[ChatMessage]] = {}
    
    def create_conversation(self, user_id: str) -> str:
        """Cria nova conversa."""
        conversation_id = f"conv_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.conversations[conversation_id] = [
            ChatMessage(
                role="system",
                content="Você é um assistente virtual especializado em eSocial, DIRF e legislação trabalhista brasileira. Responda de forma clara, objetiva e amigável.",
                timestamp=datetime.now()
            )
        ]
        return conversation_id
    
    def process_message(
        self, 
        conversation_id: str, 
        user_message: str,
        context: Optional[Dict] = None
    ) -> ChatResponse:
        """
        Processa mensagem do usuário e gera resposta.
        
        Args:
            conversation_id: ID da conversa
            user_message: Mensagem do usuário
            context: Contexto adicional (opcional)
            
        Returns:
            ChatResponse com resposta do bot
        """
        # Salva mensagem do usuário
        if conversation_id not in self.conversations:
            conversation_id = self.create_conversation("unknown")
        
        self.conversations[conversation_id].append(
            ChatMessage(role="user", content=user_message, timestamp=datetime.now())
        )
        
        # Busca na base de conhecimento
        kb_results = self.knowledge_base.search(user_message)
        
        if kb_results:
            # Retorna melhor resultado
            best_result = max(kb_results, key=lambda x: x['relevance_score'])
            response_text = best_result['response']
            confidence = best_result['relevance_score']
            sources = best_result['sources']
            
            # Ações sugeridas baseadas no tópico
            suggested_actions = self._get_suggested_actions(best_result['topic_id'])
        else:
            # Resposta genérica quando não encontra
            response_text = (
                "Desculpe, não encontrei uma resposta específica para sua pergunta.\n\n"
                "Posso ajudar com:\n"
                "• Prazos do eSocial e DIRF\n"
                "• Geração de comprovantes de rendimentos\n"
                "• Multas e penalidades\n"
                "• Como usar o sistema\n"
                "• Segurança e LGPD\n\n"
                "Por favor, reformule sua pergunta ou entre em contato com nosso suporte humano."
            )
            confidence = 0.3
            sources = []
            suggested_actions = ["Falar com atendente humano", "Ver manual completo"]
        
        # Salva resposta do bot
        self.conversations[conversation_id].append(
            ChatMessage(
                role="assistant",
                content=response_text,
                timestamp=datetime.now(),
                metadata={'confidence': confidence}
            )
        )
        
        return ChatResponse(
            message=response_text,
            confidence=confidence,
            suggested_actions=suggested_actions,
            sources=sources,
            conversation_id=conversation_id
        )
    
    def _get_suggested_actions(self, topic_id: str) -> List[str]:
        """Retorna ações sugeridas baseadas no tópico."""
        actions_map = {
            'prazo_esocial': [
                "Ver calendário completo",
                "Configurar alertas de prazo",
                "Enviar evento agora"
            ],
            'comprovante_rendimentos': [
                "Gerar comprovantes em lote",
                "Enviar por email",
                "Baixar PDF individual"
            ],
            'multas_atraso': [
                "Verificar pendências",
                "Regularizar situação",
                "Falar com contador"
            ],
            'como_usar_sistema': [
                "Assistir tutorial em vídeo",
                "Agendar treinamento",
                "Acessar documentação"
            ],
            'seguranca_dados': [
                "Ver políticas completas",
                "Baixar relatório de compliance",
                "Falar com DPO"
            ]
        }
        
        return actions_map.get(topic_id, ["Falar com atendente"])
    
    def get_conversation_history(self, conversation_id: str) -> List[ChatMessage]:
        """Retorna histórico da conversa."""
        return self.conversations.get(conversation_id, [])
    
    def escalate_to_human(self, conversation_id: str, reason: str) -> Dict:
        """Encaminha conversa para atendente humano."""
        history = self.get_conversation_history(conversation_id)
        
        ticket = {
            'ticket_id': f"TICKET_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'conversation_id': conversation_id,
            'reason': reason,
            'history': [msg.content for msg in history],
            'status': 'OPEN',
            'created_at': datetime.now()
        }
        
        # Em produção: enviaria para fila de tickets
        print(f"Ticket criado: {ticket['ticket_id']}")
        
        return ticket
