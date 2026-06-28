from scripts.doctor_instalacao import (
    STATUS_AVISO,
    STATUS_ERRO,
    STATUS_OK,
    coletar_diagnostico,
    imprimir_relatorio,
    resultado,
    verificar_arquivo,
    verificar_pasta,
)


def test_resultado_cria_dict_com_nome_status_e_detalhe():
    item = resultado("Python", STATUS_OK, "3.x")

    assert item == {
        "nome": "Python",
        "status": STATUS_OK,
        "detalhe": "3.x",
    }


def test_verificar_arquivo_retorna_ok_quando_obrigatorio_existe(tmp_path):
    arquivo = tmp_path / "requirements.txt"
    arquivo.write_text("", encoding="utf-8")

    item = verificar_arquivo(arquivo)

    assert item["status"] == STATUS_OK


def test_verificar_arquivo_retorna_erro_quando_obrigatorio_nao_existe(tmp_path):
    item = verificar_arquivo(tmp_path / "ausente.txt")

    assert item["status"] == STATUS_ERRO


def test_verificar_arquivo_retorna_aviso_quando_opcional_nao_existe(tmp_path):
    item = verificar_arquivo(tmp_path / ".env", obrigatorio=False)

    assert item["status"] == STATUS_AVISO


def test_verificar_pasta_retorna_ok_quando_pasta_existe(tmp_path):
    pasta = tmp_path / "logs"
    pasta.mkdir()

    item = verificar_pasta(pasta)

    assert item["status"] == STATUS_OK


def test_verificar_pasta_retorna_erro_quando_obrigatoria_nao_existe(tmp_path):
    item = verificar_pasta(tmp_path / "logs")

    assert item["status"] == STATUS_ERRO


def test_coletar_diagnostico_retorna_lista(tmp_path):
    resultados = coletar_diagnostico(tmp_path)

    assert isinstance(resultados, list)
    assert resultados


def test_imprimir_relatorio_nao_quebra_com_lista_simples(capsys):
    imprimir_relatorio([resultado("Teste", STATUS_OK, "detalhe")])

    saida = capsys.readouterr().out
    assert "OCR-LEITOR - Doctor de instalacao" in saida
    assert "[OK] Teste - detalhe" in saida
