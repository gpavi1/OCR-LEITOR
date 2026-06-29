#!/usr/bin/env python3
"""
reset_banco_teste.py - Limpeza segura dos registros de teste do banco MySQL.

Uso:
    python scripts/reset_banco_teste.py                           # dry-run (padrao)
    python scripts/reset_banco_teste.py --dry-run                  # explicito
    python scripts/reset_banco_teste.py --confirmar                # limpeza real
    python scripts/reset_banco_teste.py --confirmar --confirmacao "RESETAR_BANCO_TESTE"
    python scripts/reset_banco_teste.py --confirmar --limpar-integracoes
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

import database.mysql_db as db

TABELAS_CLEANUP = ["integracao_tentativas", "documentos"]
TABELAS_OPCIONAIS = ["integracoes"]
TABELAS_PROTEGIDAS = ["clientes"]
BACKUP_DIR_PADRAO = BASE_DIR / "_backup_banco_teste"
CONFIRMACAO_TEXTO = "RESETAR_BANCO_TESTE"


def listar_tabelas_existentes():
    rows = db.fetch_all(
        "SELECT TABLE_NAME FROM information_schema.TABLES "
        "WHERE TABLE_SCHEMA = DATABASE()"
    )
    return [row["TABLE_NAME"] for row in rows]


def contar_registros(tabela):
    row = db.fetch_one(f"SELECT COUNT(*) AS total FROM {tabela}")
    return row["total"] if row else 0


def exportar_tabela(tabela):
    return db.fetch_all(f"SELECT * FROM {tabela}")


def gerar_backup(destino, dados_antes, tabelas_para_limpar, tabelas_puladas, tabelas_protegidas_encontradas):
    destino.mkdir(parents=True, exist_ok=True)

    resumo = {
        "timestamp": datetime.now().isoformat(),
        "backup_dir": str(destino),
        "tabelas": {},
        "tabelas_puladas": tabelas_puladas,
        "tabelas_protegidas": tabelas_protegidas_encontradas,
    }

    for tabela in tabelas_para_limpar:
        info = dados_antes.get(tabela, {"total": 0, "dados": []})
        tem_dados = info["total"] > 0
        resumo["tabelas"][tabela] = {
            "total": info["total"],
            "salvo_em": f"{tabela}.json" if tem_dados else None,
        }
        if tem_dados:
            caminho = destino / f"{tabela}.json"
            with open(caminho, "w", encoding="utf-8") as f:
                json.dump(info["dados"], f, indent=2, ensure_ascii=False, default=str)

    with open(destino / "resumo_antes.json", "w", encoding="utf-8") as f:
        json.dump(resumo, f, indent=2, ensure_ascii=False)

    return resumo


def gerar_resumo_depois(destino, dados_depois):
    resumo = {
        "timestamp": datetime.now().isoformat(),
        "tabelas": {t: {"total": total} for t, total in dados_depois.items()},
    }
    with open(destino / "resumo_depois.json", "w", encoding="utf-8") as f:
        json.dump(resumo, f, indent=2, ensure_ascii=False)
    return resumo


def gerar_relatorio_md(destino, resumo_antes, dados_depois, modo, tabelas_limpas, erro=None):
    linhas = [
        "# Relatorio de Reset do Banco de Teste\n",
        f"**Data:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
        f"**Modo:** {modo}\n",
        "## Resumo\n",
        "| Tabela | Antes | Depois |",
        "|--------|-------|--------|",
    ]
    tabelas_resumo = resumo_antes.get("tabelas", {})
    todas_tabelas = set(tabelas_resumo.keys()) | set(dados_depois.keys())
    for nome in sorted(todas_tabelas):
        antes = tabelas_resumo.get(nome, {}).get("total", "-")
        depois = dados_depois.get(nome, "-")
        linhas.append(f"| {nome} | {antes} | {depois} |")
    linhas.append("")

    puladas = resumo_antes.get("tabelas_puladas", [])
    if puladas:
        linhas.append("## Tabelas nao alteradas por seguranca\n")
        for t in puladas:
            linhas.append(f"- {t}")
        linhas.append("")

    protegidas = resumo_antes.get("tabelas_protegidas", [])
    if protegidas:
        linhas.append("## Tabelas protegidas (nao limpas)\n")
        for t in protegidas:
            linhas.append(f"- {t}")
        linhas.append("")

    linhas.append(f"**Backup salvo em:** `{destino}`")
    if erro:
        linhas.append("")
        linhas.append("## Erro")
        linhas.append("```")
        linhas.append(str(erro))
        linhas.append("```")

    conteudo = "\n".join(linhas)
    with open(destino / "relatorio_reset_banco_teste.md", "w", encoding="utf-8") as f:
        f.write(conteudo)
    return conteudo


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Limpeza segura dos registros de teste do banco MySQL.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Exemplos:\n"
               f"  %(prog)s                              dry-run (padrao)\n"
               f"  %(prog)s --dry-run                     explicito\n"
               f"  %(prog)s --confirmar                   limpeza real\n"
               f'  %(prog)s --confirmar --confirmacao "{CONFIRMACAO_TEXTO}"\n'
               f"  %(prog)s --confirmar --limpar-integracoes\n",
    )
    parser.add_argument(
        "--dry-run", action="store_true", dest="dry_run",
        help="Modo simulacao (padrao se --confirmar nao for usado)",
    )
    parser.add_argument(
        "--confirmar", action="store_true",
        help="Confirma que deseja executar a limpeza real",
    )
    parser.add_argument(
        "--confirmacao", type=str, default="",
        help=f"Texto de confirmacao adicional (obrigatorio: '{CONFIRMACAO_TEXTO}')",
    )
    parser.add_argument(
        "--limpar-integracoes", action="store_true", dest="limpar_integracoes",
        help="Inclui tabela integracoes na limpeza (configuracoes serao perdidas)",
    )
    parser.add_argument(
        "--backup-dir", type=str, default=str(BACKUP_DIR_PADRAO),
        help=f"Diretorio de backup (padrao: {BACKUP_DIR_PADRAO})",
    )

    args = parser.parse_args(argv)

    dry_run = not args.confirmar or args.dry_run

    if args.confirmar and args.confirmacao and args.confirmacao != CONFIRMACAO_TEXTO:
        print(f"Erro: texto de confirmacao invalido. Use '{CONFIRMACAO_TEXTO}'.")
        return 1

    backup_dir = Path(args.backup_dir)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = backup_dir / f"reset_{timestamp}"

    print("=" * 60)
    print("  RESET BANCO DE TESTE - OCR LEITOR")
    print("=" * 60)
    print()

    ok, msg = db.testar_conexao()
    if not ok:
        print(f"Erro de conexao: {msg}")
        print("Verifique se o MySQL esta rodando e o .env esta configurado.")
        return 1
    print(f"* {msg}")
    print()

    todas_tabelas = listar_tabelas_existentes()
    print(f"Tabelas encontradas: {', '.join(sorted(todas_tabelas))}")
    print()

    tabelas_para_limpar = [t for t in TABELAS_CLEANUP if t in todas_tabelas]
    if args.limpar_integracoes and "integracoes" in todas_tabelas:
        tabelas_para_limpar.append("integracoes")

    tabelas_puladas = sorted(
        t for t in TABELAS_OPCIONAIS
        if t in todas_tabelas and t not in tabelas_para_limpar
    )
    tabelas_protegidas_encontradas = sorted(
        t for t in TABELAS_PROTEGIDAS if t in todas_tabelas
    )
    tabelas_desconhecidas = sorted(
        t for t in todas_tabelas
        if t not in tabelas_para_limpar
        and t not in tabelas_puladas
        and t not in tabelas_protegidas_encontradas
    )

    dados_antes = {}
    for tabela in tabelas_para_limpar:
        total = contar_registros(tabela)
        dados = exportar_tabela(tabela) if total > 0 else []
        dados_antes[tabela] = {"total": total, "dados": dados}

    print("Registros encontrados:")
    for tabela in sorted(dados_antes):
        print(f"  {tabela}: {dados_antes[tabela]['total']}")
    for tabela in tabelas_puladas:
        total = contar_registros(tabela)
        print(f"  {tabela}: {total} (nao sera limpa por seguranca)")
    for tabela in tabelas_protegidas_encontradas:
        print(f"  {tabela}: - (protegida)")
    if tabelas_desconhecidas:
        for tabela in tabelas_desconhecidas:
            print(f"  {tabela}: - (desconhecida, ignorada)")
    print()

    resumo_antes = gerar_backup(
        destino, dados_antes, tabelas_para_limpar,
        tabelas_puladas, tabelas_protegidas_encontradas,
    )
    print(f"* Backup salvo em: {destino}")
    print()

    if dry_run:
        print("Modo: DRY-RUN - NENHUM registro foi apagado.\n")
        if tabelas_para_limpar:
            print("Seria apagado:")
            for tabela in tabelas_para_limpar:
                total = dados_antes.get(tabela, {}).get("total", "?")
                print(f"  DELETE FROM {tabela}  ({total} registros)")
        if tabelas_puladas:
            print(f"  (tabelas puladas por seguranca: {', '.join(tabelas_puladas)})")
        print()
        print("Para executar a limpeza real, use --confirmar:")
        print(f'  python scripts/reset_banco_teste.py --confirmar --confirmacao "{CONFIRMACAO_TEXTO}"')
        print()

        dados_depois = {t: dados_antes[t]["total"] for t in dados_antes}
        gerar_resumo_depois(destino, dados_depois)
        gerar_relatorio_md(destino, resumo_antes, dados_depois, "DRY-RUN", tabelas_para_limpar)
        return 0

    if not args.confirmacao:
        print("Confirmacao adicional necessaria. Use:")
        print(f'  --confirmacao "{CONFIRMACAO_TEXTO}"')
        print()
        dados_depois = {t: dados_antes[t]["total"] for t in dados_antes}
        gerar_resumo_depois(destino, dados_depois)
        gerar_relatorio_md(destino, resumo_antes, dados_depois, "CANCELADO", tabelas_para_limpar)
        return 1

    print("Executando limpeza real (transacao unica)...")
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            for tabela in tabelas_para_limpar:
                print(f"  DELETE FROM {tabela}")
                cursor.execute(f"DELETE FROM {tabela}")
        print("* Limpeza concluida com sucesso.")
    except Exception as e:
        print(f"Erro durante a limpeza: {e}")
        print("Rollback executado pelo gerenciador de conexao.")
        dados_depois = {t: dados_antes[t]["total"] for t in dados_antes}
        gerar_resumo_depois(destino, dados_depois)
        gerar_relatorio_md(
            destino, resumo_antes, dados_depois, f"ERRO", tabelas_para_limpar, erro=e,
        )
        return 1

    dados_depois = {}
    for tabela in tabelas_para_limpar:
        dados_depois[tabela] = contar_registros(tabela)

    gerar_resumo_depois(destino, dados_depois)
    gerar_relatorio_md(destino, resumo_antes, dados_depois, "REAL", tabelas_para_limpar)

    print()
    print("Resumo apos limpeza:")
    for tabela in sorted(dados_depois):
        print(f"  {tabela}: {dados_depois[tabela]} registros")
    print()
    print(f"Relatorio salvo em: {destino / 'relatorio_reset_banco_teste.md'}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
