"""
Unit Tests for Core Domain Models
Fase 0: Fundação

Testes unitários para os modelos de domínio.
"""

import pytest
from decimal import Decimal
from datetime import datetime

from core.models import (
    FontePagadora,
    Beneficiario,
    Dependente,
    PensaoAlimenticia,
    InfoDepSau,
    PlanoSaude,
    PrevidenciaComplementar,
    RendimentoMensal,
    ComprovanteRendimentos,
    AmbienteType,
    SituacaoPessoa,
)


class TestFontePagadora:
    """Testes para modelo FontePagadora"""
    
    def test_criar_fonte_pagadora_valida(self):
        """Deve criar uma fonte pagadora válida"""
        fonte = FontePagadora(
            cnpj="12345678000190",
            nome="TechCorp Soluções Ltda",
        )
        
        assert fonte.cnpj == "12345678000190"
        assert fonte.nome == "TechCorp Soluções Ltda"
        assert fonte.ambiente == AmbienteType.PRODUCAO
    
    def test_validar_cnpj_valido(self):
        """Deve validar CNPJ válido"""
        fonte = FontePagadora(cnpj="12345678000190", nome="Teste")
        assert fonte.validar_cnpj() is True
    
    def test_validar_cnpj_invalido_tamanho(self):
        """Deve retornar False para CNPJ com tamanho inválido"""
        fonte = FontePagadora(cnpj="1234567800019", nome="Teste")
        assert fonte.validar_cnpj() is False
    
    def test_validar_cnpj_invalido_caracteres(self):
        """Deve retornar False para CNPJ com caracteres não numéricos"""
        fonte = FontePagadora(cnpj="1234567800019A", nome="Teste")
        assert fonte.validar_cnpj() is False
    
    def test_ambiente_pre_producao(self):
        """Deve suportar ambiente de pré-produção"""
        fonte = FontePagadora(
            cnpj="12345678000190",
            nome="Teste",
            ambiente=AmbienteType.PRE_PRODUCACAO,
        )
        assert fonte.ambiente == AmbienteType.PRE_PRODUCACAO


class TestBeneficiario:
    """Testes para modelo Beneficiario"""
    
    def test_criar_beneficiario_valido(self):
        """Deve criar um beneficiário válido"""
        benef = Beneficiario(
            cpf="12345678901",
            nome="João da Silva",
        )
        
        assert benef.cpf == "12345678901"
        assert benef.nome == "João da Silva"
        assert benef.situacao == SituacaoPessoa.ATIVA
    
    def test_validar_cpf_valido(self):
        """Deve validar CPF válido"""
        benef = Beneficiario(cpf="12345678901", nome="Teste")
        assert benef.validar_cpf() is True
    
    def test_validar_cpf_invalido_tamanho(self):
        """Deve retornar False para CPF com tamanho inválido"""
        benef = Beneficiario(cpf="1234567890", nome="Teste")
        assert benef.validar_cpf() is False
    
    def test_validar_cpf_invalido_caracteres(self):
        """Deve retornar False para CPF com caracteres não numéricos"""
        benef = Beneficiario(cpf="1234567890A", nome="Teste")
        assert benef.validar_cpf() is False
    
    def test_situacao_suspenso(self):
        """Deve suportar situação suspensa"""
        benef = Beneficiario(
            cpf="12345678901",
            nome="Teste",
            situacao=SituacaoPessoa.SUSPENSA,
        )
        assert benef.situacao == SituacaoPessoa.SUSPENSA


class TestDependente:
    """Testes para modelo Dependente"""
    
    def test_criar_dependente_valido(self):
        """Deve criar um dependente válido"""
        dep = Dependente(
            cpf="12345678901",
            nome="Maria da Silva",
            dt_nascimento="2010-05-15",
            tipo_dependente="01",
            descricao_dependente="Filho(a)",
        )
        
        assert dep.cpf == "12345678901"
        assert dep.nome == "Maria da Silva"
        assert dep.dt_nascimento == "2010-05-15"
        assert dep.tipo_dependente == "01"


class TestPensaoAlimenticia:
    """Testes para modelo PensaoAlimenticia"""
    
    def test_criar_pensao_valores_padrao(self):
        """Deve criar pensão com valores zero como padrão"""
        pensao = PensaoAlimenticia(
            cpf_beneficiario="12345678901",
            nome_beneficiario="Ex-Cônjuge",
        )
        
        assert pensao.valor_mensal == Decimal('0.00')
        assert pensao.valor_13_salario == Decimal('0.00')
        assert pensao.valor_plr == Decimal('0.00')
    
    def test_criar_pensao_com_valores(self):
        """Deve criar pensão com valores específicos"""
        pensao = PensaoAlimenticia(
            cpf_beneficiario="12345678901",
            nome_beneficiario="Ex-Cônjuge",
            valor_mensal=Decimal('1500.50'),
            valor_13_salario=Decimal('1500.50'),
            valor_plr=Decimal('0.00'),
        )
        
        assert pensao.valor_mensal == Decimal('1500.50')
        assert pensao.valor_13_salario == Decimal('1500.50')


class TestInfoDepSau:
    """Testes para modelo InfoDepSau"""
    
    def test_criar_info_dep_sau(self):
        """Deve criar informações de dependente de plano de saúde"""
        info = InfoDepSau(
            cpf_dep="12345678901",
            nm_dep="Filho Dependente",
            dt_nasc_dep="2015-03-20",
            vlr_plano=Decimal('350.00'),
        )
        
        assert info.cpf_dep == "12345678901"
        assert info.nm_dep == "Filho Dependente"
        assert info.vlr_plano == Decimal('350.00')


class TestPlanoSaude:
    """Testes para modelo PlanoSaude"""
    
    def test_criar_plano_saude_vazio(self):
        """Deve criar plano de saúde com lista vazia de dependentes"""
        plano = PlanoSaude(
            cnpj_operadora="12345678000190",
            nome_operadora="Unimed",
            registro_ans="123456",
        )
        
        assert plano.dependentes == []
        assert plano.valor_titular == Decimal('0.00')


class TestPrevidenciaComplementar:
    """Testes para modelo PrevidenciaComplementar"""
    
    def test_criar_prev_complementar(self):
        """Deve criar previdência complementar"""
        prev = PrevidenciaComplementar(
            cnpj_entidade="12345678000190",
            nome_entidade="PrevPrivada S.A.",
            tipo_previdencia="1",
            valor=Decimal('5000.00'),
        )
        
        assert prev.cnpj_entidade == "12345678000190"
        assert prev.tipo_previdencia == "1"
        assert prev.valor == Decimal('5000.00')


class TestRendimentoMensal:
    """Testes para modelo RendimentoMensal"""
    
    def test_criar_rendimento_mensal(self):
        """Deve criar rendimento mensal"""
        rend = RendimentoMensal(
            mes=1,
            ano=2025,
            rendimento_tributavel=Decimal('10000.00'),
            contribuicao_prev=Decimal('1100.00'),
            imposto_retido=Decimal('500.00'),
        )
        
        assert rend.mes == 1
        assert rend.ano == 2025
        assert rend.rendimento_tributavel == Decimal('10000.00')


class TestComprovanteRendimentos:
    """Testes para modelo ComprovanteRendimentos"""
    
    def test_criar_comprovante_vazio(self):
        """Deve criar comprovante vazio"""
        comp = ComprovanteRendimentos()
        
        assert comp.tenant_id == "default"
        assert comp.fonte_pagadora is None
        assert comp.beneficiario is None
        assert comp.dependentes == []
        assert comp.processado is False
    
    def test_criar_comprovante_completo(self):
        """Deve criar comprovante completo"""
        fonte = FontePagadora(cnpj="12345678000190", nome="Empresa X")
        benef = Beneficiario(cpf="12345678901", nome="João")
        rendimento = RendimentoMensal(
            mes=1,
            ano=2025,
            rendimento_tributavel=Decimal('10000.00'),
            contribuicao_prev=Decimal('1100.00'),
            imposto_retido=Decimal('500.00'),
        )
        
        comp = ComprovanteRendimentos(
            tenant_id="tenant-teste",
            fonte_pagadora=fonte,
            beneficiario=benef,
            rendimentos_mensais=[rendimento],
        )
        
        assert comp.tenant_id == "tenant-teste"
        assert comp.fonte_pagadora.cnpj == "12345678000190"
        assert comp.beneficiario.cpf == "12345678901"
        assert len(comp.rendimentos_mensais) == 1
    
    def test_total_rendimentos_tributaveis(self):
        """Deve calcular total de rendimentos tributáveis"""
        comp = ComprovanteRendimentos()
        comp.rendimentos_mensais = [
            RendimentoMensal(mes=1, ano=2025, rendimento_tributavel=Decimal('10000.00')),
            RendimentoMensal(mes=2, ano=2025, rendimento_tributavel=Decimal('10500.00')),
            RendimentoMensal(mes=3, ano=2025, rendimento_tributavel=Decimal('11000.00')),
        ]
        
        total = comp.total_rendimentos_tributaveis()
        assert total == Decimal('31500.00')
    
    def test_total_imposto_retido(self):
        """Deve calcular total de imposto retido"""
        comp = ComprovanteRendimentos()
        comp.rendimentos_mensais = [
            RendimentoMensal(mes=1, ano=2025, imposto_retido=Decimal('500.00')),
            RendimentoMensal(mes=2, ano=2025, imposto_retido=Decimal('550.00')),
            RendimentoMensal(mes=3, ano=2025, imposto_retido=Decimal('600.00')),
        ]
        
        total = comp.total_imposto_retido()
        assert total == Decimal('1650.00')
    
    def test_total_com_13_salario(self):
        """Deve incluir 13º salário no total"""
        comp = ComprovanteRendimentos()
        comp.rendimentos_mensais = [
            RendimentoMensal(mes=1, ano=2025, rendimento_tributavel=Decimal('10000.00')),
        ]
        comp.rendimento_13_salario = RendimentoMensal(
            mes=13,
            ano=2025,
            rendimento_tributavel=Decimal('10000.00'),
        )
        
        total = comp.total_rendimentos_tributaveis()
        assert total == Decimal('20000.00')
    
    def test_total_com_plr(self):
        """Deve incluir PLR no total"""
        comp = ComprovanteRendimentos()
        comp.rendimentos_mensais = [
            RendimentoMensal(mes=1, ano=2025, rendimento_tributavel=Decimal('10000.00')),
        ]
        comp.rendimento_plr = RendimentoMensal(
            mes=0,
            ano=2025,
            rendimento_tributavel=Decimal('5000.00'),
        )
        
        total = comp.total_rendimentos_tributaveis()
        assert total == Decimal('15000.00')


class TestAmbienteType:
    """Testes para enum AmbienteType"""
    
    def test_ambientes_disponiveis(self):
        """Deve ter os ambientes corretos"""
        assert AmbienteType.PRODUCAO.value == "PRODUCAO"
        assert AmbienteType.PRE_PRODUCACAO.value == "PRE_PRODUCACAO"


class TestSituacaoPessoa:
    """Testes para enum SituacaoPessoa"""
    
    def test_situacoes_disponiveis(self):
        """Deve ter as situações corretas"""
        assert SituacaoPessoa.ATIVA.value == "ATIVA"
        assert SituacaoPessoa.SUSPENSA.value == "SUSPENSA"
        assert SituacaoPessoa.CANCELADA.value == "CANCELADA"
