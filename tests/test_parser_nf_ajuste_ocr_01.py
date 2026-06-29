from parser_nf import parse_ocr, extrair_empresa, extrair_numero_nf, extrair_chave_acesso, extrair_vencimento_financeiro, extrair_valor_total

TEXTO_OCR_REAL = """ee ee ee eee
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
    texto = "ee ee ee eee"
    assert extrair_empresa(texto) is None


def test_parser_nao_aceita_documento_auxiliar_como_empresa():
    texto = "DOCUMENTO AUXILIAR"
    assert extrair_empresa(texto) is None


def test_parser_nao_aceita_nota_fiscal_eletronica_como_empresa():
    texto = "DE NOTA FISCAL\nELETRÔNICA"
    assert extrair_empresa(texto) is None


def test_parser_nao_aceita_chave_de_acesso_como_empresa():
    texto = "CHAVE DE ACESSO"
    assert extrair_empresa(texto) is None


def test_parser_prioriza_unilider_distribuidora_sa_como_empresa():
    dados = parse_ocr(TEXTO_OCR_REAL)
    assert dados["elemento"] == "UNILIDER DISTRIBUIDORA S/A"


def test_parser_extrai_numero_nf_1281694():
    dados = parse_ocr(TEXTO_OCR_REAL)
    assert dados["nfe"] == "1281694"


def test_parser_mantem_chave_acesso_valida():
    dados = parse_ocr(TEXTO_OCR_REAL)
    assert dados["chave"] == "33260605424008000360550010012816941717629941"
    assert len(dados["chave"]) == 44


def test_parser_nao_confunde_destinatario_com_emitente():
    dados = parse_ocr(TEXTO_OCR_REAL)
    assert dados["elemento"] != "P S CALDEIRA"
    assert dados["elemento"] == "UNILIDER DISTRIBUIDORA S/A"


def test_parser_nao_inventa_valor_total():
    dados = parse_ocr(TEXTO_OCR_REAL)
    assert dados["valor_total"] is None


def test_parser_mantem_status_parcial_para_texto_incompleto():
    dados = parse_ocr("texto curto sem dados uteis")
    assert dados["elemento"] is None
    assert dados["nfe"] is None
    assert dados["chave"] is None
    assert dados["vencimento"] is None
    assert dados["valor_total"] is None


def test_parser_comportamento_seguro_texto_vazio():
    dados = parse_ocr("")
    assert dados["elemento"] is None
    assert dados["nfe"] is None
    assert dados["vencimento"] is None
    assert dados["valor_total"] is None


def test_parser_comportamento_seguro_none():
    dados = parse_ocr(None)
    assert dados["elemento"] is None
    assert dados["nfe"] is None
    assert dados["vencimento"] is None
    assert dados["valor_total"] is None


def test_parser_registra_fonte_e_confianca():
    dados = parse_ocr(TEXTO_OCR_REAL)
    assert "raw" in dados
    assert dados["raw"] is not None
