from scripts.preparar_instalacao_local import (
    PASTAS_OPERACIONAIS,
    imprimir_relatorio,
    main,
    preparar_pastas,
    resultado,
    verificar_arquivos_locais,
)


def test_preparar_pastas_dry_run_nao_cria_pastas(tmp_path):
    resultados = preparar_pastas(tmp_path, confirmar=False)

    assert {item["acao"] for item in resultados} == {"CRIAR"}
    for nome_pasta in PASTAS_OPERACIONAIS:
        assert not (tmp_path / nome_pasta).exists()


def test_preparar_pastas_confirmar_cria_pastas_operacionais(tmp_path):
    resultados = preparar_pastas(tmp_path, confirmar=True)

    assert {item["acao"] for item in resultados} == {"CRIADO"}
    for nome_pasta in PASTAS_OPERACIONAIS:
        assert (tmp_path / nome_pasta).is_dir()


def test_verificar_arquivos_locais_avisa_quando_env_nao_existe(tmp_path):
    resultados = verificar_arquivos_locais(tmp_path)

    env = [item for item in resultados if item["alvo"].endswith(".env")][0]
    assert env["acao"] == "AVISO"


def test_verificar_arquivos_locais_avisa_quando_settings_nao_existe(tmp_path):
    resultados = verificar_arquivos_locais(tmp_path)

    settings = [item for item in resultados if item["alvo"].endswith("settings.json")][0]
    assert settings["acao"] == "AVISO"


def test_main_retorna_1_quando_base_dir_nao_existe(tmp_path):
    retorno = main(["--base-dir", str(tmp_path / "ausente")])

    assert retorno == 1


def test_main_dry_run_com_base_dir_valido_retorna_0(tmp_path):
    retorno = main(["--base-dir", str(tmp_path)])

    assert retorno == 0
    for nome_pasta in PASTAS_OPERACIONAIS:
        assert not (tmp_path / nome_pasta).exists()


def test_main_confirmar_cria_pastas_em_tmp_path(tmp_path):
    retorno = main(["--base-dir", str(tmp_path), "--confirmar"])

    assert retorno == 0
    for nome_pasta in PASTAS_OPERACIONAIS:
        assert (tmp_path / nome_pasta).is_dir()


def test_imprimir_relatorio_nao_quebra(capsys):
    imprimir_relatorio([resultado("OK", "alvo", "detalhe")])

    saida = capsys.readouterr().out
    assert "OCR-LEITOR - Preparacao local" in saida
    assert "[OK] alvo - detalhe" in saida
