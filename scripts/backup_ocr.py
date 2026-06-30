import argparse
import json
import os
import zipfile
from datetime import datetime
from pathlib import Path


TIPO_MANIFEST = "ocr_leitor_backup"
VERSAO_MANIFEST = "1.0"
TABELAS_BANCO = ["clientes", "documentos", "integracoes", "integracao_tentativas"]
PASTAS_OPERACIONAIS = ["input", "output", "processed", "erro", "logs", "exports"]
NUNCA_INCLUIR = [
    ".env em claro",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    "dist",
    "backups",
    "_backup",
    "_backup_testes",
    "_backup_banco_teste",
    "*.pyc",
    "*.log com segredo detectado",
]


def agora_iso():
    return datetime.now().replace(microsecond=0).isoformat()


def nome_backup(agora=None):
    momento = agora or datetime.now()
    return f"OCR-LEITOR-BACKUP-{momento:%Y%m%d-%H%M%S}.zip"


def caminho_relativo_zip(path):
    return str(path).replace("\\", "/")


def carregar_env(path):
    valores = {}
    if not path.is_file():
        return valores
    for linha in path.read_text(encoding="utf-8").splitlines():
        texto = linha.strip()
        if not texto or texto.startswith("#") or "=" not in texto:
            continue
        chave, valor = texto.split("=", 1)
        valores[chave.strip()] = valor.strip().strip('"').strip("'")
    return valores


def chave_sensivel(chave):
    chave_lower = chave.lower()
    termos = ["token", "password", "senha", "secret", "key"]
    return any(termo in chave_lower for termo in termos)


def mascarar_env(path):
    linhas = []
    if not path.is_file():
        return "# .env ausente\n"
    for linha in path.read_text(encoding="utf-8").splitlines():
        if not linha.strip() or linha.lstrip().startswith("#") or "=" not in linha:
            linhas.append(linha)
            continue
        chave, valor = linha.split("=", 1)
        if chave_sensivel(chave) and valor.strip():
            linhas.append(f"{chave}=***")
        else:
            linhas.append(linha)
    return "\n".join(linhas) + "\n"


def conteudo_log_com_segredo(path):
    if path.suffix.lower() != ".log":
        return False
    try:
        texto = path.read_text(encoding="utf-8", errors="ignore").lower()
    except OSError:
        return True
    termos = ["token", "authorization", "bearer", "secret", "senha", "password"]
    return any(termo in texto for termo in termos)


def caminho_deve_ser_ignorado(path, project_root):
    partes = set(path.relative_to(project_root).parts)
    ignorados = {
        ".venv",
        "__pycache__",
        ".pytest_cache",
        "dist",
        "backups",
        "_backup",
        "_backup_testes",
        "_backup_banco_teste",
    }
    if partes & ignorados:
        return True
    if path.suffix.lower() == ".pyc":
        return True
    if conteudo_log_com_segredo(path):
        return True
    return False


def coletar_arquivos_operacionais(project_root, manifest):
    itens = []
    for pasta in PASTAS_OPERACIONAIS:
        origem = project_root / pasta
        destino_dir = Path("arquivos") / pasta
        manifest["pastas_incluidas"].append(caminho_relativo_zip(destino_dir) + "/")
        itens.append((origem, destino_dir, True))
        if not origem.is_dir():
            manifest["avisos"].append(f"Pasta operacional ausente: {pasta}")
            continue
        for arquivo in origem.rglob("*"):
            if not arquivo.is_file():
                continue
            if caminho_deve_ser_ignorado(arquivo, project_root):
                manifest["avisos"].append(f"Arquivo ignorado por seguranca: {arquivo.relative_to(project_root)}")
                continue
            rel = arquivo.relative_to(origem)
            itens.append((arquivo, destino_dir / rel, False))
            manifest["arquivos_incluidos"].append(caminho_relativo_zip(destino_dir / rel))
    return itens


def exportar_banco_json(project_root):
    env = carregar_env(project_root / ".env")
    if not env.get("DB_PASSWORD"):
        return None, {"status": "aviso", "mensagem": "DB_PASSWORD ausente; banco nao exportado."}

    try:
        import mysql.connector

        conexao = mysql.connector.connect(
            host=env.get("DB_HOST", "localhost"),
            port=int(env.get("DB_PORT", "3306")),
            database=env.get("DB_NAME", "ocr_leitor"),
            user=env.get("DB_USER", "ocr_app"),
            password=env.get("DB_PASSWORD", ""),
            charset="utf8mb4",
            use_unicode=True,
        )
        cursor = conexao.cursor(dictionary=True)
        dados = {}
        avisos = []
        for tabela in TABELAS_BANCO:
            try:
                cursor.execute(f"SELECT * FROM `{tabela}`")
                dados[tabela] = cursor.fetchall()
            except Exception as exc:
                dados[tabela] = []
                avisos.append(f"Tabela {tabela} nao exportada: {exc}")
        cursor.close()
        conexao.close()
        resumo = {"status": "ok", "tabelas": list(dados.keys()), "avisos": avisos}
        if avisos:
            resumo["status"] = "aviso"
        return dados, resumo
    except Exception as exc:
        return None, {"status": "aviso", "mensagem": f"Banco nao exportado: {exc}"}


def montar_plano(project_root, destino, incluir_env_mascarado=False, sem_banco=False):
    project_root = Path(project_root).resolve()
    destino = Path(destino).resolve()
    manifest = {
        "tipo": TIPO_MANIFEST,
        "versao_manifest": VERSAO_MANIFEST,
        "criado_em": agora_iso(),
        "project_root": str(project_root),
        "incluiu_env_mascarado": bool(incluir_env_mascarado),
        "incluiu_banco": not sem_banco,
        "banco_status": "ignorado" if sem_banco else "aviso",
        "pastas_incluidas": [],
        "arquivos_incluidos": [],
        "avisos": [],
        "nunca_incluir": list(NUNCA_INCLUIR),
    }
    arquivos = coletar_arquivos_operacionais(project_root, manifest)

    schema = project_root / "database" / "schema.sql"
    if schema.is_file():
        arquivos.append((schema, Path("database") / "schema.sql", False))
        manifest["arquivos_incluidos"].append("database/schema.sql")
    else:
        manifest["avisos"].append("database/schema.sql ausente")

    settings = project_root / "config" / "settings.json"
    if settings.is_file():
        arquivos.append((settings, Path("config") / "settings.json", False))
        manifest["arquivos_incluidos"].append("config/settings.json")

    banco_dados = None
    if sem_banco:
        banco_resumo = {"status": "ignorado", "mensagem": "Backup de banco ignorado por --sem-banco."}
    else:
        banco_dados, banco_resumo = exportar_banco_json(project_root)
        manifest["banco_status"] = banco_resumo.get("status", "aviso")
        if banco_resumo.get("status") != "ok":
            manifest["avisos"].append(banco_resumo.get("mensagem", "Banco exportado com avisos."))

    zip_path = destino / nome_backup()
    return {
        "project_root": project_root,
        "destino": destino,
        "zip_path": zip_path,
        "manifest": manifest,
        "arquivos": arquivos,
        "env_mascarado": mascarar_env(project_root / ".env") if incluir_env_mascarado else None,
        "banco_dados": banco_dados,
        "banco_resumo": banco_resumo,
    }


def diagnostico_texto(plano):
    manifest = plano["manifest"]
    linhas = [
        "OCR-LEITOR - Diagnostico de backup",
        f"Criado em: {manifest['criado_em']}",
        f"Project root: {manifest['project_root']}",
        f"Banco: {manifest['banco_status']}",
        f"Pastas incluidas: {len(manifest['pastas_incluidas'])}",
        f"Arquivos incluidos: {len(manifest['arquivos_incluidos'])}",
        "Avisos:",
    ]
    linhas.extend(f"- {aviso}" for aviso in manifest["avisos"])
    return "\n".join(linhas) + "\n"


def gerar_zip(plano):
    plano["destino"].mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(plano["zip_path"], "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(plano["manifest"], indent=2, ensure_ascii=False, default=str))
        zf.writestr("suporte/diagnostico.txt", diagnostico_texto(plano))
        zf.writestr("database/resumo.json", json.dumps(plano["banco_resumo"], indent=2, ensure_ascii=False, default=str))
        if plano["banco_dados"] is not None:
            zf.writestr("database/dados.json", json.dumps(plano["banco_dados"], indent=2, ensure_ascii=False, default=str))
        if plano["env_mascarado"] is not None:
            zf.writestr("config/env_mascarado.txt", plano["env_mascarado"])
        for origem, destino_zip, eh_pasta in plano["arquivos"]:
            nome = caminho_relativo_zip(destino_zip)
            if eh_pasta:
                zf.writestr(nome.rstrip("/") + "/", "")
            elif origem.is_file():
                zf.write(origem, nome)
    return plano["zip_path"]


def imprimir_plano(plano, dry_run):
    acao = "DRY-RUN" if dry_run else "BACKUP"
    print(f"OCR-LEITOR - {acao} operacional")
    print(f"Destino: {plano['zip_path']}")
    print(f"Banco: {plano['manifest']['banco_status']}")
    for pasta in plano["manifest"]["pastas_incluidas"]:
        print(f"Pasta: {pasta}")
    for arquivo in plano["manifest"]["arquivos_incluidos"]:
        print(f"Arquivo: {arquivo}")
    for aviso in plano["manifest"]["avisos"]:
        print(f"AVISO: {aviso}")


def criar_parser():
    parser = argparse.ArgumentParser(description="Backup operacional seguro do OCR-LEITOR")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--confirmar", action="store_true")
    parser.add_argument("--destino")
    parser.add_argument("--incluir-env-mascarado", action="store_true")
    parser.add_argument("--sem-banco", action="store_true")
    parser.add_argument("--project-root")
    return parser


def main(argv=None):
    args = criar_parser().parse_args(argv)
    project_root = Path(args.project_root).resolve() if args.project_root else Path(__file__).resolve().parents[1]
    destino = Path(args.destino).resolve() if args.destino else project_root / "backups"
    plano = montar_plano(
        project_root,
        destino,
        incluir_env_mascarado=args.incluir_env_mascarado,
        sem_banco=args.sem_banco,
    )

    if args.dry_run or not args.confirmar:
        imprimir_plano(plano, dry_run=True)
        if not args.confirmar:
            print("ZIP real nao gerado. Use --confirmar para criar backup.")
        return 0

    caminho = gerar_zip(plano)
    imprimir_plano(plano, dry_run=False)
    print(f"Backup criado: {caminho}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
