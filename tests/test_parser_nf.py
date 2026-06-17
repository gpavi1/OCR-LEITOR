from parser_nf import parse_ocr, extrair_chave_acesso, extrair_vencimento_financeiro


def test_extrai_chave_quebrada_por_espacos():
    texto = """
    DANFE
    CHAVE DE ACESSO
    3524 0612 3456 7800 0195 5500 1000 1234 5612 3456 7890
    """
    chave = extrair_chave_acesso(texto)
    assert chave == "35240612345678000195550010001234561234567890"
    assert len(chave) == 44


def test_nao_pega_data_de_emissao_sem_contexto_financeiro():
    texto = """
    DATA DE EMISSAO: 10/06/2026
    DATA DE SAIDA: 10/06/2026
    TRANSPORTE: 11/06/2026
    """
    assert extrair_vencimento_financeiro(texto) is None


def test_pega_vencimento_com_contexto_financeiro():
    texto = """
    FATURA
    Valor: 150,00
    VENCIMENTO: 20/07/2026
    """
    assert extrair_vencimento_financeiro(texto) == "20/07/2026"


def test_ignora_emissao_e_pega_vencimento():
    texto = """
    DATA DE EMISSAO: 10/06/2026

    BOLETO BANCARIO
    PAGAMENTO ATE O VENCIMENTO: 25/07/2026
    """
    assert extrair_vencimento_financeiro(texto) == "25/07/2026"


def test_parse_ocr_mantem_campos_principais():
    texto = """
    EMPRESA TESTE LTDA
    NF 123456
    CHAVE DE ACESSO 3524 0612 3456 7800 0195 5500 1000 1234 5612 3456 7890
    DUPLICATA VENCIMENTO 30/08/2026
    """
    dados = parse_ocr(texto)
    assert dados["elemento"] == "EMPRESA TESTE LTDA"
    assert dados["nfe"] == "123456"
    assert dados["chave"] == "35240612345678000195550010001234561234567890"
    assert dados["vencimento"] == "30/08/2026"
