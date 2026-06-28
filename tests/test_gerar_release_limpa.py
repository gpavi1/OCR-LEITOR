import subprocess
from pathlib import Path

from scripts.gerar_release_limpa import (
    NOME_ZIP_PADRAO,
    detectar_base_dir,
    gerar_zip_git_archive,
    imprimir_relatorio,
    interpretar_worktree_limpo,
    main,
    resultado,
    validar_nome_zip,
)


def test_validar_nome_zip_aceita_zip():
    valido, erro = validar_nome_zip("teste.zip")
    assert valido
    assert erro == ""


def test_validar_nome_zip_rejeita_sem_zip():
    valido, erro = validar_nome_zip("teste.txt")
    assert not valido
    assert "zip" in erro.lower()


def test_validar_nome_zip_rejeita_separador():
    valido, _ = validar_nome_zip("../teste.zip")
    assert not valido
    valido2, _ = validar_nome_zip("pasta/teste.zip")
    assert not valido2
    valido3, _ = validar_nome_zip("pasta\\teste.zip")
    assert not valido3


def test_detectar_base_dir_retorna_caminho_existente():
    caminho = detectar_base_dir()
    assert Path(caminho).is_dir()


def test_main_retorna_1_quando_base_dir_nao_existe(tmp_path):
    retorno = main(["--base-dir", str(tmp_path / "ausente")])
    assert retorno == 1


def test_main_retorna_1_em_dry_run_sem_git(tmp_path):
    retorno = main(["--base-dir", str(tmp_path)])
    assert retorno == 1


def test_interpretar_worktree_limpo_com_vazio():
    assert interpretar_worktree_limpo("") is True
    assert interpretar_worktree_limpo("   ") is True


def test_interpretar_worktree_limpo_com_sujeira():
    assert interpretar_worktree_limpo(" M foo.txt") is False
    assert interpretar_worktree_limpo("?? novo.py\n") is False


def test_gerar_zip_nao_chamado_em_dry_run(tmp_path):
    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True, timeout=30)
    retorno = main(["--base-dir", str(tmp_path), "--destino-dir", str(tmp_path / "dist")])
    assert retorno == 0
    assert not (tmp_path / "dist").exists()


def test_imprimir_relatorio_nao_quebra(capsys):
    imprimir_relatorio([resultado("OK", "alvo", "detalhe")])
    saida = capsys.readouterr().out
    assert "OCR-LEITOR - Release limpa" in saida
    assert "[OK] alvo - detalhe" in saida
