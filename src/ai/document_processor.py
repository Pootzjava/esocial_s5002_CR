"""
Módulo de OCR e NLP para processamento inteligente de documentos.
Extrai dados de comprovantes de rendimentos em PDF/Imagem usando técnicas de IA.
"""
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ExtractedData:
    """Dados extraídos de um documento."""
    document_type: str
    employee_name: str
    employee_cpf: str
    employer_name: str
    employer_cnpj: str
    reference_year: int
    total_income: float
    tax_withheld: float
    contributions: float
    confidence_score: float
    raw_text: str
    extraction_timestamp: datetime


class DocumentProcessor:
    """Processador de documentos com OCR e NLP."""
    
    def __init__(self):
        # Padrões regex para extração
        self.patterns = {
            'cpf': r'\d{3}\.\d{3}\.\d{3}-\d{2}',
            'cnpj': r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}',
            'currency': r'R\$\s*[\d\.]+,\d{2}',
            'year': r'\b(19|20)\d{2}\b',
            'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        }
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extrai texto de um arquivo PDF.
        Nota: Implementação simplificada - em produção usaria PyPDF2 ou pdfplumber.
        
        Args:
            pdf_path: Caminho do arquivo PDF
            
        Returns:
            Texto extraído do PDF
        """
        # Simulação para testes - em produção integraria com biblioteca OCR
        return "Texto simulado do PDF"
    
    def extract_text_from_image(self, image_path: str) -> str:
        """
        Extrai texto de uma imagem usando OCR.
        Nota: Implementação simplificada - em produção usaria Tesseract ou AWS Textract.
        
        Args:
            image_path: Caminho da imagem
            
        Returns:
            Texto extraído da imagem
        """
        # Simulação para testes
        return "Texto simulado da imagem via OCR"
    
    def parse_currency(self, value_str: str) -> float:
        """
        Converte string de moeda para float.
        
        Args:
            value_str: String no formato R$ 1.234,56
            
        Returns:
            Valor como float
        """
        if not value_str:
            return 0.0
        
        # Remove R$ e espaços
        clean_value = re.sub(r'R\$\s*', '', value_str)
        # Substitui vírgula por ponto e remove pontos de milhar
        clean_value = clean_value.replace('.', '').replace(',', '.')
        
        try:
            return float(clean_value)
        except ValueError:
            return 0.0
    
    def extract_cpf(self, text: str) -> Optional[str]:
        """Extrai CPF do texto."""
        matches = re.findall(self.patterns['cpf'], text)
        return matches[0] if matches else None
    
    def extract_cnpj(self, text: str) -> Optional[str]:
        """Extrai CNPJ do texto."""
        matches = re.findall(self.patterns['cnpj'], text)
        return matches[0] if matches else None
    
    def extract_currency_values(self, text: str) -> List[float]:
        """Extrai todos os valores monetários do texto."""
        matches = re.findall(self.patterns['currency'], text)
        return [self.parse_currency(m) for m in matches]
    
    def extract_year(self, text: str) -> Optional[int]:
        """Extrai ano de referência."""
        matches = re.findall(self.patterns['year'], text)
        return int(matches[-1]) if matches else None  # Pega o último ano encontrado
    
    def classify_document(self, text: str) -> str:
        """
        Classifica o tipo de documento baseado no conteúdo.
        
        Args:
            text: Texto do documento
            
        Returns:
            Tipo de documento (INCOME_STATEMENT, TAX_RETURN, etc.)
        """
        text_lower = text.lower()
        
        if 'rendimentos' in text_lower and 'imposto de renda' in text_lower:
            return 'INCOME_STATEMENT'
        elif 'dirf' in text_lower:
            return 'DIRF'
        elif 'esocial' in text_lower:
            return 'ESOCIAL_EVENT'
        else:
            return 'UNKNOWN'
    
    def calculate_confidence(self, extracted_fields: Dict[str, Any]) -> float:
        """
        Calcula score de confiança baseado nos campos extraídos.
        
        Args:
            extracted_fields: Dicionário com campos extraídos
            
        Returns:
            Score de confiança entre 0.0 e 1.0
        """
        required_fields = ['employee_cpf', 'employer_cnpj', 'total_income', 'reference_year']
        present_fields = sum(1 for field in required_fields if extracted_fields.get(field))
        
        base_confidence = present_fields / len(required_fields)
        
        # Bônus se tiver todos os campos obrigatórios
        if present_fields == len(required_fields):
            base_confidence = min(1.0, base_confidence + 0.2)
        
        return round(base_confidence, 2)
    
    def process_document(self, file_path: str, file_type: str = 'pdf') -> ExtractedData:
        """
        Processa documento completo e extrai dados estruturados.
        
        Args:
            file_path: Caminho do arquivo
            file_type: Tipo do arquivo (pdf, image, png, jpg)
            
        Returns:
            ExtractedData com informações estruturadas
        """
        # Extração de texto
        if file_type.lower() in ['pdf']:
            raw_text = self.extract_text_from_pdf(file_path)
        else:
            raw_text = self.extract_text_from_image(file_path)
        
        # Extração de campos
        extracted_fields = {
            'document_type': self.classify_document(raw_text),
            'employee_cpf': self.extract_cpf(raw_text),
            'employer_cnpj': self.extract_cnpj(raw_text),
            'currency_values': self.extract_currency_values(raw_text),
            'reference_year': self.extract_year(raw_text),
        }
        
        # Inferir valores
        currency_values = extracted_fields['currency_values']
        total_income = currency_values[0] if len(currency_values) > 0 else 0.0
        tax_withheld = currency_values[1] if len(currency_values) > 1 else 0.0
        contributions = currency_values[2] if len(currency_values) > 2 else 0.0
        
        # Calcular confiança
        confidence = self.calculate_confidence(extracted_fields)
        
        return ExtractedData(
            document_type=extracted_fields['document_type'],
            employee_name="",  # Requer NLP mais avançado
            employee_cpf=extracted_fields['employee_cpf'] or "",
            employer_name="",  # Requer NLP mais avançado
            employer_cnpj=extracted_fields['employer_cnpj'] or "",
            reference_year=extracted_fields['reference_year'] or datetime.now().year,
            total_income=total_income,
            tax_withheld=tax_withheld,
            contributions=contributions,
            confidence_score=confidence,
            raw_text=raw_text,
            extraction_timestamp=datetime.now()
        )
    
    def batch_process(self, file_paths: List[tuple]) -> List[ExtractedData]:
        """
        Processa múltiplos documentos em lote.
        
        Args:
            file_paths: Lista de tuplas (caminho, tipo)
            
        Returns:
            Lista de ExtractedData
        """
        results = []
        for file_path, file_type in file_paths:
            try:
                result = self.process_document(file_path, file_type)
                results.append(result)
            except Exception as e:
                # Log error e continua processando
                print(f"Erro ao processar {file_path}: {str(e)}")
                continue
        
        return results
