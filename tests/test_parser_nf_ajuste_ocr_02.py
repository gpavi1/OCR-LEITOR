from parser_nf import (
    parse_ocr,
    extrair_empresa,
    extrair_numero_nf,
    extrair_chave_acesso,
    extrair_vencimento_financeiro,
    extrair_valor_total,
)

TEXTO_FIXTURE_1_MERCADO_ALFA = """DOCUMENTO FICTICIO PARA TESTE OCR - SEM VALOR FISCAL

DANFE - DOCUMENTO AUXILIAR DE NOTA FISCAL ELETRONIC.

MERCADO TESTE ALFA LTDA
AVENIDA DAS AMOSTRAS, 1000 - CENTRO - CIDADE TESTE/BR
CNP: 12.345.678/0001-90 IE: 123456789

NF-e No.

100001

SERIE: 1

CHAVE DE ACESSO

3526 0612 3456 7800 0190 5500 1000 1000 0112 3456 7890

DESTINATARIO / REMETENTE

RAZAO SOCIAL: CLIENTE TESTE PADRAO LTDA
CNPJ/CPF: 98.765.432/0001-10 DATA EMISSAO: 29/06/2026

CALCULO DO IMPOSTO

BASE DE CALCULO ICMS R$ 1.200,00
VALOR DO ICMS R$ 216,00
VALOR TOTAL DOS PRODUTOS R$ 1.200,00
VALOR TOTAL DA NOTA RSE. 256,75
DUPLICATA / FATURA

VENCIMENTO: 15/07/2026 VALOR: R$ 1.250,75

DADOS DOS PRODUTOS / SERVICOS

coD DESCRICAO QTD VL UNIT TOTAL
001 PRODUTO TESTE A - CAIXA 12 UN 10 50,00 500,00
002 PRODUTO TESTE B - FARDO 6 UN 5 100,00 500,00
003 PRODUTO TESTE C - UNIDADE 4 50,00 200,00"""

TEXTO_FIXTURE_2_NFSE_SERVICOS_BETA = """DOCUMENTO FICTICIO PARA TESTE OCR - SEM VALOR FISCAL

SERVICOS BETA TECNOLOGIA ME NOTA FISCAL DE SERVICOS

RUA DOS TESTES, 456 - SALA 10 NUMERO NFS-e: 20260077
CNPJ: 23.456.789/0001-01

MUNICIPIO: CIDADE EXEMPLO EMISSAO: 29/06/2026

COMPETENCIA: 06/2026

CODIGO DE VERIFICACAO
BETA-2026-000077-TESTE

TOMADOR DOS SERVICOS

CLIENTE MODELO SERVICOS LTDA
CNPJ: 34.567.890/0001-12

DESCRICAO DOS SERVICOS

PRESTACAO DE SERVICOS DE SUPORTE TECNICO, MANUTENCAO PREVENTIVA E
CONSULTORIA EM SISTEMAS PARA TESTE DE OCR.

VALOR DOS SERVICOS R$ 875,40
VENCIMENTO 30/07/2026
OBSERVACOES

Documento sem validade fiscal. Dados ficticios para validacao de OCR."""

TEXTO_FIXTURE_3_DANFE_ATACADO_GAMMA = """DOCUMENTO FICTICIO PARA TESTE OCR - SEM VALOR FISCAL

RECEBEMOS DE ATACADO GAMMA S/A OS PRODUTOS CONSTANTES DA NF-e INDICADA ABAIXO

ATACADO GAMMA S/A NF-e

BAIRRO INDUSTRIAL - CIDADE TESTE

CNPJ: 45.678.901/0001-23 SERIE 3

RODOVIA DO TESTE, KM 12 - GALPAO 3 No. 987654

CHAVE DE ACESSO
3526 0645 6789 0100 0123 5500 3000 9876 5498 7654 3210

DESTINATARIO

MERCADO COMPRADOR MODELO LTDA
CNPJ: 56.789.012/0001-34 DATA EMISSAO: 29/06/2026

TOTAIS

TOTAL DOS PRODUTOS: R$ 2.340,00

FRETE: R$ 60,00 DESCONTO: R$ 100,00
TOTAL GERAL DA NOTA: R$ 2.300,00

COBRANCA
PARCELA 001 VENC. 05/08/2026 VALOR R$ 2.300,00

PRODUTOS

0010 ITEM GAMMA TESTE 01 CX 2 600,00
0020 ITEM GAMMA TESTE 02 UN 5 180,00
0030 ITEM GAMMA TESTE 03 KG 3 80,00"""

# ── Fixture 1: Mercado Alfa ──────────────────────────────────────────────────


def test_mercado_alfa_mantem_empresa_correta():
    dados = parse_ocr(TEXTO_FIXTURE_1_MERCADO_ALFA)
    assert dados["elemento"] == "MERCADO TESTE ALFA LTDA"


def test_mercado_alfa_captura_nf_100001():
    dados = parse_ocr(TEXTO_FIXTURE_1_MERCADO_ALFA)
    assert dados["nfe"] == "100001"


def test_mercado_alfa_mantem_chave_correta():
    dados = parse_ocr(TEXTO_FIXTURE_1_MERCADO_ALFA)
    assert dados["chave"] == "35260612345678000190550010001000011234567890"
    assert len(dados["chave"]) == 44


def test_mercado_alfa_captura_vencimento():
    dados = parse_ocr(TEXTO_FIXTURE_1_MERCADO_ALFA)
    assert dados["vencimento"] == "15/07/2026"


def test_mercado_alfa_captura_valor_duplicata():
    dados = parse_ocr(TEXTO_FIXTURE_1_MERCADO_ALFA)
    assert dados["valor_total"] == 1250.75


# ── Fixture 2: Serviços Beta ────────────────────────────────────────────────


def test_servicos_beta_captura_emitente():
    dados = parse_ocr(TEXTO_FIXTURE_2_NFSE_SERVICOS_BETA)
    assert dados["elemento"] == "SERVICOS BETA TECNOLOGIA ME"


def test_servicos_beta_nao_captura_tomador_como_empresa():
    dados = parse_ocr(TEXTO_FIXTURE_2_NFSE_SERVICOS_BETA)
    assert dados["elemento"] != "CLIENTE MODELO SERVICOS LTDA"


def test_servicos_beta_captura_nfs_e_20260077():
    dados = parse_ocr(TEXTO_FIXTURE_2_NFSE_SERVICOS_BETA)
    assert dados["nfe"] == "20260077"


def test_servicos_beta_nao_gera_chave_falsa():
    dados = parse_ocr(TEXTO_FIXTURE_2_NFSE_SERVICOS_BETA)
    assert dados["chave"] is None


def test_servicos_beta_captura_valor_servicos():
    dados = parse_ocr(TEXTO_FIXTURE_2_NFSE_SERVICOS_BETA)
    assert dados["valor_total"] == 875.40


def test_servicos_beta_captura_vencimento():
    dados = parse_ocr(TEXTO_FIXTURE_2_NFSE_SERVICOS_BETA)
    assert dados["vencimento"] == "30/07/2026"


# ── Fixture 3: Atacado Gamma ────────────────────────────────────────────────


def test_atacado_gamma_captura_emitente():
    dados = parse_ocr(TEXTO_FIXTURE_3_DANFE_ATACADO_GAMMA)
    assert dados["elemento"] == "ATACADO GAMMA S/A"


def test_atacado_gamma_nao_captura_destinatario_como_empresa():
    dados = parse_ocr(TEXTO_FIXTURE_3_DANFE_ATACADO_GAMMA)
    assert dados["elemento"] != "MERCADO COMPRADOR MODELO LTDA"


def test_atacado_gamma_captura_nf_987654():
    dados = parse_ocr(TEXTO_FIXTURE_3_DANFE_ATACADO_GAMMA)
    assert dados["nfe"] == "987654"


def test_atacado_gamma_mantem_chave_correta():
    dados = parse_ocr(TEXTO_FIXTURE_3_DANFE_ATACADO_GAMMA)
    assert dados["chave"] == "35260645678901000123550030009876549876543210"
    assert len(dados["chave"]) == 44


def test_atacado_gamma_captura_total_geral():
    dados = parse_ocr(TEXTO_FIXTURE_3_DANFE_ATACADO_GAMMA)
    assert dados["valor_total"] == 2300.00


def test_atacado_gamma_captura_vencimento_abreviado():
    dados = parse_ocr(TEXTO_FIXTURE_3_DANFE_ATACADO_GAMMA)
    assert dados["vencimento"] == "05/08/2026"


# ── Comportamento seguro legado (herdado de AJUSTE-OCR-01) ──────────────────


TEXTO_UNILIDER = """ee ee ee eee
PS CALDEIRA Rémnessa: 0081736897 - Ordem: 0001805803

DOCUMENTO AUXILIAR
DE NOTA FISCAL
ELETRÔNICA

UNILIDER DISTRIBUIDORA S/A

CHAVE DE ACESSO
AV. EMIGDIO MAIA SANTOS, 1362 - .
3326 0605 4240 0800 0360 5500 1001 2816 9417 1762 9941
ARMAZ.1 * 1281694

SÉRIE: 1
Venda merc.adq.receb.de terceiros/Vnd mer.adq.rec.
233260265155151 2026-06-11 21:50:47

CNPJ
05.424.008/0003-60

DESTINATARIO/REMETENTE
RAZAO SOCIAL CNPJ/CPF DATA EMISSAO
P S CALDEIRA 03.360.571/0001-25 11/06/2026"""


def test_parser_nao_aceita_ee_ee_ee_eee_como_empresa():
    assert extrair_empresa("ee ee ee eee") is None


def test_parser_nao_aceita_documento_auxiliar_como_empresa():
    assert extrair_empresa("DOCUMENTO AUXILIAR") is None


def test_parser_nao_aceita_nota_fiscal_eletronica_como_empresa():
    assert extrair_empresa("DE NOTA FISCAL\nELETRÔNICA") is None


def test_parser_nao_aceita_chave_de_acesso_como_empresa():
    assert extrair_empresa("CHAVE DE ACESSO") is None


def test_parser_prioriza_unilider_distribuidora_sa():
    dados = parse_ocr(TEXTO_UNILIDER)
    assert dados["elemento"] == "UNILIDER DISTRIBUIDORA S/A"


def test_parser_extrai_numero_nf_unilider():
    dados = parse_ocr(TEXTO_UNILIDER)
    assert dados["nfe"] == "1281694"


def test_parser_mantem_chave_acesso_valida_unilider():
    dados = parse_ocr(TEXTO_UNILIDER)
    assert dados["chave"] == "33260605424008000360550010012816941717629941"
    assert len(dados["chave"]) == 44


def test_parser_nao_confunde_destinatario_com_emitente_unilider():
    dados = parse_ocr(TEXTO_UNILIDER)
    assert dados["elemento"] != "P S CALDEIRA"
    assert dados["elemento"] == "UNILIDER DISTRIBUIDORA S/A"


def test_parser_nao_inventa_valor_total_sem_contexto():
    dados = parse_ocr(TEXTO_UNILIDER)
    assert dados["valor_total"] is None


def test_parser_nao_inventa_valor_quando_sem_valor_claro():
    texto = "EMPRESA EXEMPLO LTDA\nNF 123\nVENCIMENTO 30/12/2026"
    dados = parse_ocr(texto)
    assert dados["valor_total"] is None


def test_parser_nao_inventa_chave_quando_sem_contexto_real():
    texto = "EMPRESA EXEMPLO LTDA\nNF 123\nVENCIMENTO 30/12/2026"
    dados = parse_ocr(texto)
    assert dados["chave"] is None


def test_parser_comportamento_seguro_texto_vazio():
    dados = parse_ocr("")
    assert dados["elemento"] is None
    assert dados["nfe"] is None
    assert dados["chave"] is None
    assert dados["vencimento"] is None
    assert dados["valor_total"] is None


def test_parser_comportamento_seguro_none():
    dados = parse_ocr(None)
    assert dados["elemento"] is None
    assert dados["nfe"] is None
    assert dados["chave"] is None
    assert dados["vencimento"] is None
    assert dados["valor_total"] is None
