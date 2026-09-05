"""
Test Factories using Factory Boy
Fase 0: Fundação

Factories para criação de objetos de teste.
"""

import factory
from datetime import datetime
from decimal import Decimal
from faker import Faker

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

fake = Faker("pt_BR")


class FontePagadoraFactory(factory.Factory):
    """Factory para FontePagadora"""
    class Meta:
        model = FontePagadora
    
    cnpj = factory.LazyFunction(lambda: fake.cpf().replace("-", "").replace(".", "")[:14])
    nome = factory.LazyFunction(lambda: fake.company())
    id_esocial = None
    ambiente = AmbienteType.PRODUCAO


class BeneficiarioFactory(factory.Factory):
    """Factory para Beneficiario"""
    class Meta:
        model = Beneficiario
    
    cpf = factory.LazyFunction(lambda: fake.cpf().replace("-", "").replace(".", "")[:11])
    nome = factory.LazyFunction(lambda: fake.name())
    dt_nascimento = factory.LazyFunction(lambda: fake.date_of_birth(minimum_age=18, maximum_age=70).strftime("%Y-%m-%d"))
    situacao = SituacaoPessoa.ATIVA


class DependenteFactory(factory.Factory):
    """Factory para Dependente"""
    class Meta:
        model = Dependente
    
    cpf = factory.LazyFunction(lambda: fake.cpf().replace("-", "").replace(".", "")[:11])
    nome = factory.LazyFunction(lambda: fake.first_name())
    dt_nascimento = factory.LazyFunction(lambda: fake.date_of_birth(minimum_age=0, maximum_age=25).strftime("%Y-%m-%d"))
    tipo_dependente = "01"  # Filho
    descricao_dependente = "Filho(a)"


class PensaoAlimenticiaFactory(factory.Factory):
    """Factory para PensaoAlimenticia"""
    class Meta:
        model = PensaoAlimenticia
    
    cpf_beneficiario = factory.LazyFunction(lambda: fake.cpf().replace("-", "").replace(".", "")[:11])
    nome_beneficiario = factory.LazyFunction(lambda: fake.name())
    valor_mensal = factory.LazyFunction(lambda: Decimal(str(round(fake.pyfloat(left_digits=3, right_digits=2, positive=True), 2))))
    valor_13_salario = factory.LazyFunction(lambda: Decimal('0.00'))
    valor_plr = factory.LazyFunction(lambda: Decimal('0.00'))


class InfoDepSauFactory(factory.Factory):
    """Factory para InfoDepSau"""
    class Meta:
        model = InfoDepSau
    
    cpf_dep = factory.LazyFunction(lambda: fake.cpf().replace("-", "").replace(".", "")[:11])
    nm_dep = factory.LazyFunction(lambda: fake.first_name())
    dt_nasc_dep = factory.LazyFunction(lambda: fake.date_of_birth(minimum_age=0, maximum_age=60).strftime("%Y-%m-%d"))
    vlr_plano = factory.LazyFunction(lambda: Decimal(str(round(fake.pyfloat(left_digits=3, right_digits=2, positive=True), 2))))


class PlanoSaudeFactory(factory.Factory):
    """Factory para PlanoSaude"""
    class Meta:
        model = PlanoSaude
    
    cnpj_operadora = factory.LazyFunction(lambda: fake.cpf().replace("-", "").replace(".", "")[:14])
    nome_operadora = factory.LazyFunction(lambda: fake.company())
    registro_ans = factory.LazyFunction(lambda: str(fake.random_number(digits=6)))
    valor_titular = factory.LazyFunction(lambda: Decimal(str(round(fake.pyfloat(left_digits=3, right_digits=2, positive=True), 2))))
    dependentes = factory.List([])


class PrevidenciaComplementarFactory(factory.Factory):
    """Factory para PrevidenciaComplementar"""
    class Meta:
        model = PrevidenciaComplementar
    
    cnpj_entidade = factory.LazyFunction(lambda: fake.cpf().replace("-", "").replace(".", "")[:14])
    nome_entidade = factory.LazyFunction(lambda: fake.company())
    tipo_previdencia = "1"  # PGBL
    valor = factory.LazyFunction(lambda: Decimal(str(round(fake.pyfloat(left_digits=4, right_digits=2, positive=True), 2))))


class RendimentoMensalFactory(factory.Factory):
    """Factory para RendimentoMensal"""
    class Meta:
        model = RendimentoMensal
    
    mes = factory.Sequence(lambda n: n + 1)  # 1 a 12
    ano = 2025
    rendimento_tributavel = factory.LazyFunction(lambda: Decimal(str(round(fake.pyfloat(left_digits=4, right_digits=2, positive=True), 2))))
    contribuicao_prev = factory.LazyFunction(lambda: Decimal(str(round(fake.pyfloat(left_digits=3, right_digits=2, positive=True), 2))))
    imposto_retido = factory.LazyFunction(lambda: Decimal(str(round(fake.pyfloat(left_digits=3, right_digits=2, positive=True), 2))))
    rendimento_isento = factory.LazyFunction(lambda: Decimal('0.00'))
    rendimento_exclusivo = factory.LazyFunction(lambda: Decimal('0.00'))


class ComprovanteRendimentosFactory(factory.Factory):
    """Factory para ComprovanteRendimentos"""
    class Meta:
        model = ComprovanteRendimentos
    
    id = None
    tenant_id = "default"
    fonte_pagadora = factory.SubFactory(FontePagadoraFactory)
    beneficiario = factory.SubFactory(BeneficiarioFactory)
    dependentes = factory.List([])
    pensoes_alimenticias = factory.List([])
    planos_saude = factory.List([])
    prev_complementar = factory.List([])
    rendimentos_mensais = factory.List([])
    rendimento_13_salario = None
    rendimento_plr = None
    processado = False
    arquivo_xml_origem = None
    arquivo_pdf_gerado = None
