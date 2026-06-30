"""
VALIDACAO-INTEGRACAO-OPERACIONAL-OCR-01.

Testes do validador operacional central da integracao Monday.
Nao chama API externa.
Nao usa banco real.
Nao usa token real.
"""

import os
import sys
import inspect

ROOT_DIR = Path = None
try:
    ROOT_DIR = Path = __file__
except NameError:
    pass

if ROOT_DIR:
    import pathlib
    ROOT_DIR = pathlib.Path(__file__).resolve().parents[1]
    if str(ROOT_DIR) not in sys.path:
        sys.path.insert(0, str(ROOT_DIR))


from services.validador_integracao_monday import (
    validar_integracao_monday,
    _classificar_valor_config,
)

DOCUMENTO_APTO = {
    "id": 1,
    "cliente_id": 1,
    "empresa": "Empresa Teste Ltda",
    "numero_nf": "123456",
    "chave_acesso": "12345678901234567890123456789012345678901234",
    "vencimento": "2026-07-15",
    "valor_total": "1500.00",
    "status": "pendente_integracao",
    "revisado": True,
    "revisado_por": "operador_local",
    "observacao_revisao": "Conferido",
    "json_path": "/tmp/test.json",
}

CONFIG_COMPLETA = {
    "token": "eyJhbGciOiJIUzI1NiJ9.token_real",
    "board_id": "1234567890",
    "mapa_colunas": {
        "empresa": "texto_empresa",
        "numero_nf": "numero_nf",
        "chave_acesso": "chave_acesso",
        "vencimento": "data_vencimento",
        "valor_total": "valor_total",
        "observacao_revisao": "observacao",
    },
}

COLUNAS_INCOMPLETAS = {
    "empresa": "texto_empresa",
    "numero_nf": "numero_nf",
}


def test_1_validacao_retorna_dict_com_chaves_esperadas():
    """validar_integracao_monday retorna dict com chaves esperadas."""
    resultado = validar_integracao_monday()
    chaves_esperadas = {
        "config_ok", "documento_ok", "pode_simular",
        "pode_enviar", "bloqueios", "avisos", "proximos_passos",
    }
    assert isinstance(resultado, dict)
    assert chaves_esperadas.issubset(resultado.keys())


def test_2_config_completa_retorna_config_ok_true():
    """Config completa retorna config_ok=True."""
    resultado = validar_integracao_monday(
        token=CONFIG_COMPLETA["token"],
        board_id=CONFIG_COMPLETA["board_id"],
        mapa_colunas=CONFIG_COMPLETA["mapa_colunas"],
    )
    assert resultado["config_ok"] is True


def test_3_token_ausente_retorna_config_ok_false():
    """Token ausente retorna config_ok=False."""
    resultado = validar_integracao_monday(
        token="",
        board_id=CONFIG_COMPLETA["board_id"],
        mapa_colunas=CONFIG_COMPLETA["mapa_colunas"],
    )
    assert resultado["config_ok"] is False
    assert any("MONDAY_API_TOKEN" in b for b in resultado["bloqueios"])


def test_4_token_placeholder_retorna_config_ok_false():
    """Token placeholder retorna config_ok=False."""
    resultado = validar_integracao_monday(
        token="cole seu token aqui",
        board_id=CONFIG_COMPLETA["board_id"],
        mapa_colunas=CONFIG_COMPLETA["mapa_colunas"],
    )
    assert resultado["config_ok"] is False
    assert any("MONDAY_API_TOKEN" in b for b in resultado["bloqueios"])


def test_5_board_id_ausente_retorna_config_ok_false():
    """Board ID ausente retorna config_ok=False."""
    resultado = validar_integracao_monday(
        token=CONFIG_COMPLETA["token"],
        board_id="",
        mapa_colunas=CONFIG_COMPLETA["mapa_colunas"],
    )
    assert resultado["config_ok"] is False
    assert any("MONDAY_BOARD_ID" in b for b in resultado["bloqueios"])


def test_6_coluna_obrigatoria_ausente_retorna_config_ok_false():
    """Coluna obrigatoria ausente retorna config_ok=False."""
    resultado = validar_integracao_monday(
        token=CONFIG_COMPLETA["token"],
        board_id=CONFIG_COMPLETA["board_id"],
        mapa_colunas=COLUNAS_INCOMPLETAS,
    )
    assert resultado["config_ok"] is False
    assert any("Coluna obrigatoria" in b for b in resultado["bloqueios"])


def test_7_documento_apto_retorna_documento_ok_true():
    """Documento apto retorna documento_ok=True."""
    resultado = validar_integracao_monday(documento=DOCUMENTO_APTO)
    assert resultado["documento_ok"] is True


def test_8_documento_apto_retorna_pode_simular_true():
    """Documento apto retorna pode_simular=True."""
    resultado = validar_integracao_monday(documento=DOCUMENTO_APTO)
    assert resultado["pode_simular"] is True


def test_9_documento_nao_revisado_retorna_documento_ok_false():
    """Documento nao revisado retorna documento_ok=False."""
    doc = dict(DOCUMENTO_APTO)
    doc["revisado"] = False
    resultado = validar_integracao_monday(documento=doc)
    assert resultado["documento_ok"] is False


def test_10_documento_com_status_errado_retorna_documento_ok_false():
    """Documento com status errado retorna documento_ok=False."""
    doc = dict(DOCUMENTO_APTO)
    doc["status"] = "pendente_revisao"
    resultado = validar_integracao_monday(documento=doc)
    assert resultado["documento_ok"] is False


def test_11_documento_apto_config_completa_retorna_pode_enviar_true():
    """Documento apto + config completa retorna pode_enviar=True."""
    resultado = validar_integracao_monday(
        documento=DOCUMENTO_APTO,
        token=CONFIG_COMPLETA["token"],
        board_id=CONFIG_COMPLETA["board_id"],
        mapa_colunas=CONFIG_COMPLETA["mapa_colunas"],
    )
    assert resultado["pode_enviar"] is True


def test_12_documento_apto_config_incompleta_retorna_pode_enviar_false():
    """Documento apto + config incompleta retorna pode_enviar=False."""
    resultado = validar_integracao_monday(
        documento=DOCUMENTO_APTO,
        token="",
        board_id=CONFIG_COMPLETA["board_id"],
        mapa_colunas=CONFIG_COMPLETA["mapa_colunas"],
    )
    assert resultado["pode_enviar"] is False


def test_13_config_incompleta_permite_simular_mas_com_aviso():
    """Documento apto + config incompleta ainda pode simular, mas com aviso."""
    resultado = validar_integracao_monday(
        documento=DOCUMENTO_APTO,
        token="",
        board_id=CONFIG_COMPLETA["board_id"],
        mapa_colunas=CONFIG_COMPLETA["mapa_colunas"],
    )
    assert resultado["pode_simular"] is True
    assert any("Simulacao permitida" in a for a in resultado["avisos"])


def test_14_tentativa_sucesso_bloqueia_envio():
    """Tentativa monday_envio_sucesso bloqueia envio."""
    tentativas = [
        {"status": "dry_run_apto", "destino_externo_id": None},
        {"status": "monday_envio_sucesso", "destino_externo_id": "item_123"},
    ]
    resultado = validar_integracao_monday(
        documento=DOCUMENTO_APTO,
        token=CONFIG_COMPLETA["token"],
        board_id=CONFIG_COMPLETA["board_id"],
        mapa_colunas=CONFIG_COMPLETA["mapa_colunas"],
        tentativas=tentativas,
    )
    assert resultado["pode_enviar"] is False
    assert any("envio registrado" in b for b in resultado["bloqueios"])


def test_15_destino_externo_id_preenchido_bloqueia_envio():
    """Tentativa com destino_externo_id preenchido bloqueia envio."""
    tentativas = [
        {"status": "dry_run_apto", "destino_externo_id": "monday-dryrun-documento-1"},
        {"status": "monday_envio_falha", "destino_externo_id": "item_parcial_456"},
    ]
    resultado = validar_integracao_monday(
        documento=DOCUMENTO_APTO,
        token=CONFIG_COMPLETA["token"],
        board_id=CONFIG_COMPLETA["board_id"],
        mapa_colunas=CONFIG_COMPLETA["mapa_colunas"],
        tentativas=tentativas,
    )
    assert resultado["pode_enviar"] is False
    assert any("destino externo" in b for b in resultado["bloqueios"])


def test_16_falha_sem_destino_nao_bloqueia_vira_aviso():
    """monday_envio_falha sem destino_externo_id nao bloqueia, vira aviso."""
    tentativas = [
        {"status": "monday_envio_falha", "destino_externo_id": None},
        {"status": "monday_envio_bloqueado", "destino_externo_id": None},
    ]
    resultado = validar_integracao_monday(
        documento=DOCUMENTO_APTO,
        token=CONFIG_COMPLETA["token"],
        board_id=CONFIG_COMPLETA["board_id"],
        mapa_colunas=CONFIG_COMPLETA["mapa_colunas"],
        tentativas=tentativas,
    )
    assert resultado["pode_enviar"] is True
    assert any("Falhas anteriores" in a for a in resultado["avisos"])


def test_17_modulo_nao_contem_requests():
    """services/validador_integracao_monday.py nao contem import requests."""
    import services.validador_integracao_monday as v
    source = inspect.getsource(v)
    assert "import requests" not in source
    assert "from requests" not in source


def test_18_modulo_nao_contem_urllib():
    """services/validador_integracao_monday.py nao contem import urllib."""
    import services.validador_integracao_monday as v
    source = inspect.getsource(v)
    assert "import urllib" not in source
    assert "from urllib" not in source


def test_19_app_importa_validador():
    """web/app.py importa validar_integracao_monday."""
    import web.app as app
    source = inspect.getsource(app)
    assert "from services.validador_integracao_monday import validar_integracao_monday" in source


def test_20_app_usa_validador_na_rota_dryrun():
    """web/app.py usa validar_integracao_monday na rota dry-run."""
    import web.app as app
    source = inspect.getsource(app)
    assert "validar_integracao_monday" in source
    assert "pode_simular" in source


def test_21_app_usa_validador_na_rota_envio_real():
    """web/app.py usa validar_integracao_monday na rota envio real."""
    import web.app as app
    source = inspect.getsource(app)
    assert "pode_enviar" in source


def test_22_template_contem_pronto_para_integrar():
    """integracoes.html contem 'Pronto para integrar?'."""
    import pathlib
    template_path = pathlib.Path(__file__).resolve().parents[1] / "web" / "templates" / "integracoes.html"
    content = template_path.read_text(encoding="utf-8")
    assert "Pronto para integrar?" in content


def test_23_template_condiciona_enviar_monday():
    """integracoes.html condiciona Enviar para Monday a pode_enviar."""
    import pathlib
    template_path = pathlib.Path(__file__).resolve().parents[1] / "web" / "templates" / "integracoes.html"
    content = template_path.read_text(encoding="utf-8")
    assert "pode_enviar" in content


def test_24_documentacao_existe():
    """Documentacao VALIDACAO_INTEGRACAO_OPERACIONAL.md existe."""
    import pathlib
    doc_path = pathlib.Path(__file__).resolve().parents[1] / "docs" / "operacao" / "VALIDACAO_INTEGRACAO_OPERACIONAL.md"
    assert doc_path.exists()


def test_25_documentacao_sem_token_real():
    """Documentacao nao contem token real, JWT real ou Authorization real."""
    import pathlib
    doc_path = pathlib.Path(__file__).resolve().parents[1] / "docs" / "operacao" / "VALIDACAO_INTEGRACAO_OPERACIONAL.md"
    content = doc_path.read_text(encoding="utf-8")
    assert "eyJhbGci" not in content
    assert "Authorization:" not in content
    assert "Bearer " not in content


def test_26_classificar_valor_config():
    """_classificar_valor_config classifica corretamente."""
    assert _classificar_valor_config(None) == "AUSENTE"
    assert _classificar_valor_config("") == "AUSENTE"
    assert _classificar_valor_config("  ") == "AUSENTE"
    assert _classificar_valor_config("cole seu token") == "PLACEHOLDER"
    assert _classificar_valor_config("exemplo_token") == "PLACEHOLDER"
    assert _classificar_valor_config("nao_cole_aqui") == "PLACEHOLDER"
    assert _classificar_valor_config("token_valido_123") == "CONFIGURADO"


def test_27_validacao_sem_documento_retorna_bloqueios():
    """Validacao sem documento retorna bloqueios."""
    resultado = validar_integracao_monday()
    assert resultado["documento_ok"] is False
    assert any("Nenhum documento" in b for b in resultado["bloqueios"])
    assert resultado["pode_simular"] is False
    assert resultado["pode_enviar"] is False


def test_28_services_module_init_exists():
    """services/__init__.py existe."""
    import pathlib
    init_path = pathlib.Path(__file__).resolve().parents[1] / "services" / "__init__.py"
    assert init_path.exists()
