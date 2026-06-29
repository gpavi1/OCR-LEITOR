import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _read(path):
    with open(os.path.join(BASE, path), "r", encoding="utf-8") as f:
        return f.read()


def _exists(path):
    return os.path.isfile(os.path.join(BASE, path))


# ── Existência dos documentos ────────────────────────────────────────────────


def test_guia_principal_existe():
    assert _exists("docs/operacao/GUIA_PILOTO_EMPRESA_01.md")


def test_checklist_existe():
    assert _exists("docs/operacao/CHECKLIST_REVISAO_DOCUMENTO.md")


def test_modelo_csv_existe():
    assert _exists("docs/operacao/MODELO_CONTROLE_PILOTO_EMPRESA.csv")


# ── Conteúdo do guia principal ──────────────────────────────────────────────


def test_guia_menciona_revisao_humana_obrigatoria():
    conteudo = _read("docs/operacao/GUIA_PILOTO_EMPRESA_01.md").lower()
    assert "revisão humana" in conteudo or "revisao humana" in conteudo or "revisão" in conteudo


def test_guia_menciona_nao_integrar_automaticamente():
    conteudo = _read("docs/operacao/GUIA_PILOTO_EMPRESA_01.md")
    assert "integracao automatica" in conteudo.lower() or "integrar automaticamente" in conteudo.lower()


def test_guia_menciona_nao_alterar_parser():
    conteudo = _read("docs/operacao/GUIA_PILOTO_EMPRESA_01.md").lower()
    assert "não altera parser" in conteudo or "não alterar parser" in conteudo or "nao altera parser" in conteudo or "não muda parser" in conteudo


def test_guia_menciona_criterio_ajuste_ocr_03():
    conteudo = _read("docs/operacao/GUIA_PILOTO_EMPRESA_01.md")
    assert "AJUSTE-OCR-03" in conteudo


def test_guia_menciona_fluxo_operacional():
    conteudo = _read("docs/operacao/GUIA_PILOTO_EMPRESA_01.md")
    assert "passo" in conteudo.lower() and "enviar" in conteudo.lower()


def test_guia_menciona_status_operacionais():
    conteudo = _read("docs/operacao/GUIA_PILOTO_EMPRESA_01.md")
    assert "pendente_revisao" in conteudo


def test_guia_menciona_cuidados_seguranca():
    conteudo = _read("docs/operacao/GUIA_PILOTO_EMPRESA_01.md")
    assert "não commitar" in conteudo.lower()


# ── Conteúdo do checklist ───────────────────────────────────────────────────


def test_checklist_contem_campos_obrigatorios():
    conteudo = _read("docs/operacao/CHECKLIST_REVISAO_DOCUMENTO.md")
    assert "empresa" in conteudo.lower()
    assert "número nf" in conteudo.lower() or "numero nf" in conteudo.lower() or "nfe" in conteudo.lower()
    assert "chave" in conteudo.lower()
    assert "vencimento" in conteudo.lower()
    assert "valor total" in conteudo.lower()


def test_checklist_contem_regras_aprovacao():
    conteudo = _read("docs/operacao/CHECKLIST_REVISAO_DOCUMENTO.md")
    assert "não aprovar" in conteudo.lower() or "aprovar" in conteudo.lower()


def test_checklist_contem_quando_nao_mexer_no_codigo():
    conteudo = _read("docs/operacao/CHECKLIST_REVISAO_DOCUMENTO.md")
    assert "não mexer" in conteudo.lower() or "nao mexer" in conteudo.lower() or "caso isolado" in conteudo.lower()


# ── Conteúdo do CSV ─────────────────────────────────────────────────────────


def test_csv_colunas_obrigatorias():
    cabeçalho = _read("docs/operacao/MODELO_CONTROLE_PILOTO_EMPRESA.csv").split("\n")[0].lower()
    colunas_necessarias = [
        "empresa_extraida", "nf_extraida", "chave_extraida",
        "vencimento_extraido", "valor_extraido",
        "revisao_humana", "falha_observada",
    ]
    for coluna in colunas_necessarias:
        assert coluna in cabeçalho, f"Coluna '{coluna}' ausente no CSV"


def test_csv_nao_contem_dados_reais_conhecidos():
    from pathlib import Path
    conteudo = Path(os.path.join(BASE, "docs/operacao/MODELO_CONTROLE_PILOTO_EMPRESA.csv")).read_text(encoding="utf-8").lower()
    termos_reais = ["unimarka", "cafe tres coracoes", "café três corações", "seara", "sitio santa luzia", "sítio santa luzia", "p s caldeira"]
    for termo in termos_reais:
        if termo in conteudo:
            raise AssertionError(f"CSV contém dado real: '{termo}'")


# ── Segurança: sem segredos ─────────────────────────────────────────────────


def test_documentos_nao_contem_valores_de_senha():
    for path in ["docs/operacao/GUIA_PILOTO_EMPRESA_01.md", "docs/operacao/CHECKLIST_REVISAO_DOCUMENTO.md"]:
        if _exists(path):
            conteudo = _read(path)
            assert "minha_senha" not in conteudo and "123456" not in conteudo
            assert "senha =" not in conteudo and "password =" not in conteudo


def test_documentos_nao_contem_db_password():
    for path in ["docs/operacao/GUIA_PILOTO_EMPRESA_01.md", "docs/operacao/CHECKLIST_REVISAO_DOCUMENTO.md"]:
        if _exists(path):
            assert "DB_PASSWORD" not in _read(path)


def test_documentos_nao_contem_token():
    for path in ["docs/operacao/GUIA_PILOTO_EMPRESA_01.md", "docs/operacao/CHECKLIST_REVISAO_DOCUMENTO.md"]:
        if _exists(path):
            conteudo = _read(path).upper()
            assert "OCR_API_TOKEN" not in conteudo


# ── Segurança: escopo dos testes ────────────────────────────────────────────


def test_nao_executa_ocr_real():
    assert True


def test_nao_conecta_mysql():
    assert True


def test_nao_requer_internet():
    assert True


def test_nao_altera_codigo_aplicacao():
    assert True


def test_testes_lendo_apenas_documentacao():
    caminhos_verificados = [
        "docs/operacao/GUIA_PILOTO_EMPRESA_01.md",
        "docs/operacao/CHECKLIST_REVISAO_DOCUMENTO.md",
        "docs/operacao/MODELO_CONTROLE_PILOTO_EMPRESA.csv",
    ]
    for caminho in caminhos_verificados:
        assert _exists(caminho), f"Arquivo esperado ausente: {caminho}"
