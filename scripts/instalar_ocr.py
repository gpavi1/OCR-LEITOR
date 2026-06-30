import argparse
import shutil
import subprocess
import sys
from pathlib import Path

try:
    from scripts.caminhos_instalacao import (
        CAMINHO_PADRAO_CLIENTE,
        CAMINHO_PADRAO_DEMO,
        classificar_caminho_instalacao,
        detectar_instalacao_existente,
        obter_estrutura_pastas_recomendada,
    )
except ModuleNotFoundError:
    from caminhos_instalacao import (
        CAMINHO_PADRAO_CLIENTE,
        CAMINHO_PADRAO_DEMO,
        classificar_caminho_instalacao,
        detectar_instalacao_existente,
        obter_estrutura_pastas_recomendada,
    )


PASTAS_PRESERVADAS_UPDATE = [
    "input",
    "output",
    "processed",
    "erro",
    "logs",
    "exports",
    "backups",
]


def obter_root_projeto():
    return Path(__file__).resolve().parents[1]


def acao(tipo, descricao, **dados):
    item = {"tipo": tipo, "descricao": descricao}
    item.update(dados)
    return item


def resolver_destino(destino, padrao):
    return Path(destino or padrao)


def montar_acoes_demo(destino=None):
    destino = resolver_destino(destino, CAMINHO_PADRAO_DEMO)
    classificacao = classificar_caminho_instalacao(destino, modo="demo")
    acoes = [
        acao("validacao", "Validar caminho para modo demo", destino=str(destino), resultado=classificacao),
    ]
    for aviso in classificacao["avisos"]:
        acoes.append(acao("aviso", aviso))
    for bloqueio in classificacao["bloqueios"]:
        acoes.append(acao("erro", bloqueio))

    if str(destino).lower() == CAMINHO_PADRAO_CLIENTE.lower():
        acoes.append(acao("aviso", "Modo demo recebeu caminho recomendado de cliente real."))

    for pasta in obter_estrutura_pastas_recomendada("demo"):
        acoes.append(acao("criar_pasta", f"Criar pasta {pasta}", caminho=str(destino / pasta)))
    acoes.extend([
        acao("criar_env_demo", "Criar .env ficticio seguro para demonstracao", caminho=str(destino / ".env")),
        acao("orientar", "Usar banco ocr_leitor_demo e nao configurar token real."),
        acao("orientar", "Abrir OCR-LEITOR.cmd para operacao diaria apos a preparacao."),
    ])
    return acoes


def montar_acoes_cliente(destino=None):
    destino = resolver_destino(destino, CAMINHO_PADRAO_CLIENTE)
    classificacao = classificar_caminho_instalacao(destino, modo="cliente")
    acoes = [
        acao("validacao", "Validar caminho para modo cliente", destino=str(destino), resultado=classificacao),
    ]
    for bloqueio in classificacao["bloqueios"]:
        acoes.append(acao("erro", bloqueio))
    for aviso in classificacao["avisos"]:
        acoes.append(acao("aviso", aviso))

    for pasta in obter_estrutura_pastas_recomendada("cliente"):
        acoes.append(acao("criar_pasta", f"Preparar pasta {pasta}", caminho=str(destino / pasta)))
    acoes.extend([
        acao("verificar_python", "Validar Python disponivel"),
        acao("orientar", "Validar Tesseract com scripts/validador_tesseract.py."),
        acao("orientar", "Validar MySQL com scripts/validador_mysql.py."),
        acao("orientar", "Criar .venv se necessario e instalar requirements."),
        acao("orientar", "Configurar .env com scripts/configurar_ambiente.py."),
        acao("comando_verificacao", "Rodar doctor de instalacao", script="doctor_instalacao.py"),
        acao("orientar", "Checklist final: doctor OK, Tesseract OK, MySQL OK e OCR-LEITOR.cmd abrindo o menu."),
    ])
    return acoes


def montar_acoes_update(destino=None):
    destino = resolver_destino(destino, CAMINHO_PADRAO_CLIENTE)
    classificacao = classificar_caminho_instalacao(destino, modo="update")
    instalacao = detectar_instalacao_existente(destino)
    acoes = [
        acao("validacao", "Validar caminho para modo update", destino=str(destino), resultado=classificacao),
    ]

    if str(destino).lower() == CAMINHO_PADRAO_DEMO.lower():
        acoes.append(acao("erro", "Update cliente nao permitido sobre pasta demo."))
    if not instalacao["existe"]:
        acoes.append(acao("erro", "Update exige instalação existente."))
    if not (destino / ".env").is_file():
        acoes.append(acao("erro", "Update exige instalação existente com .env."))
    for bloqueio in classificacao["bloqueios"]:
        if bloqueio not in {"Update exige instalação existente."}:
            acoes.append(acao("erro", bloqueio))

    acoes.append(acao("backup", "Gerar backup operacional obrigatorio antes do update", destino=str(destino)))
    for nome in [".env", "config/settings.json", "banco MySQL", *PASTAS_PRESERVADAS_UPDATE]:
        acoes.append(acao("preservar", f"Preservar {nome}", alvo=nome))
    acoes.extend([
        acao("orientar", "Copiar arquivos novos apenas a partir do pacote local/release, sem git pull e sem internet."),
        acao("comando_verificacao", "Rodar validacao pos-update com doctor", script="doctor_instalacao.py"),
    ])
    return acoes


def montar_acoes_verificar(project_root=None):
    root = Path(project_root or obter_root_projeto())
    return [
        acao("comando_verificacao", "Rodar doctor de instalacao", script="doctor_instalacao.py", project_root=str(root)),
        acao("comando_verificacao", "Validar Tesseract", script="validador_tesseract.py", project_root=str(root)),
        acao("comando_verificacao", "Validar MySQL", script="validador_mysql.py", project_root=str(root)),
    ]


def criar_estrutura_pastas(destino):
    destino = Path(destino)
    for pasta in obter_estrutura_pastas_recomendada():
        (destino / pasta).mkdir(parents=True, exist_ok=True)


def criar_env_demo(destino):
    destino = Path(destino)
    env_path = destino / ".env"
    if env_path.exists():
        return False
    destino.mkdir(parents=True, exist_ok=True)
    conteudo = "\n".join([
        "# OCR-LEITOR DEMO - valores ficticios",
        "WEB_SECRET_KEY=demo-local-nao-usar-producao",
        "WEB_USERNAME=admin",
        "WEB_PASSWORD=demo",
        "DB_HOST=localhost",
        "DB_PORT=3306",
        "DB_NAME=ocr_leitor_demo",
        "DB_USER=ocr_demo",
        "DB_PASSWORD=demo",
        "MONDAY_API_TOKEN=",
        "MONDAY_BOARD_ID=",
        "DEBUG=false",
        "",
    ])
    env_path.write_text(conteudo, encoding="utf-8")
    return True


def validar_pre_requisitos_cliente(destino):
    destino = Path(destino)
    return {
        "destino": str(destino),
        "python": bool(shutil.which("python") or sys.executable),
        "caminho": classificar_caminho_instalacao(destino, modo="cliente"),
    }


def validar_pre_requisitos_update(destino):
    destino = Path(destino)
    instalacao = detectar_instalacao_existente(destino)
    return {
        "destino": str(destino),
        "instalacao_existente": instalacao["existe"],
        "env_existe": (destino / ".env").is_file(),
        "backup_obrigatorio": True,
    }


def executar_comando_python(script, project_root=None):
    root = Path(project_root or obter_root_projeto())
    python = root / ".venv" / "Scripts" / "python.exe"
    executavel = str(python) if python.is_file() else sys.executable
    caminho_script = root / "scripts" / script
    if not caminho_script.is_file():
        print(f"AVISO: script nao encontrado: {caminho_script}")
        return 1
    return subprocess.run([executavel, str(caminho_script)], cwd=str(root), timeout=120).returncode


def executar_backup_update(destino, project_root=None):
    root = Path(project_root or obter_root_projeto())
    python = root / ".venv" / "Scripts" / "python.exe"
    executavel = str(python) if python.is_file() else sys.executable
    script = root / "scripts" / "backup_ocr.py"
    if not script.is_file():
        print("ERRO: backup_ocr.py nao encontrado; update abortado.")
        return 1
    comando = [
        executavel,
        str(script),
        "--project-root",
        str(destino),
        "--destino",
        str(Path(destino) / "backups"),
        "--confirmar",
        "--incluir-env-mascarado",
    ]
    return subprocess.run(comando, cwd=str(root), timeout=120).returncode


def executar_acoes(acoes, confirmar=False, dry_run=False, project_root=None):
    encontrou_erro = False
    for item in acoes:
        tipo = item["tipo"]
        print(f"[{tipo}] {item['descricao']}")
        if tipo == "erro":
            encontrou_erro = True
    if encontrou_erro:
        print("Operacao abortada por validacao de seguranca.")
        return 1

    aplicar = confirmar and not dry_run
    for item in acoes:
        tipo = item["tipo"]
        if tipo == "criar_pasta":
            if aplicar:
                Path(item["caminho"]).mkdir(parents=True, exist_ok=True)
            else:
                print(f"DRY-RUN: criaria {item['caminho']}")
        elif tipo == "criar_env_demo":
            if aplicar:
                criado = criar_env_demo(Path(item["caminho"]).parent)
                print(".env demo criado." if criado else ".env existente preservado.")
            else:
                print(f"DRY-RUN: criaria {item['caminho']}")
        elif tipo == "backup":
            if aplicar:
                retorno = executar_backup_update(Path(item["destino"]), project_root=project_root)
                if retorno != 0:
                    print("ERRO: backup obrigatorio falhou; update abortado.")
                    return retorno
            else:
                print("DRY-RUN: backup operacional obrigatorio seria executado antes do update.")
        elif tipo == "verificar_python":
            if not (shutil.which("python") or sys.executable):
                print("ERRO: Python nao encontrado.")
                return 1
        elif tipo == "comando_verificacao":
            if dry_run:
                print(f"DRY-RUN: executaria {item['script']}")
            else:
                retorno = executar_comando_python(item["script"], project_root=item.get("project_root") or project_root)
                if retorno != 0:
                    print(f"AVISO: {item['script']} retornou codigo {retorno}.")
    if not confirmar and not dry_run:
        print("Nenhuma alteracao real aplicada. Use --confirmar para aplicar acoes permitidas.")
    return 0


def criar_parser():
    parser = argparse.ArgumentParser(description="Instalador compacto seguro do OCR-LEITOR")
    subparsers = parser.add_subparsers(dest="modo")
    for modo in ["demo", "cliente", "update", "verificar"]:
        subparser = subparsers.add_parser(modo)
        subparser.add_argument("--dry-run", action="store_true")
        subparser.add_argument("--confirmar", action="store_true")
        subparser.add_argument("--destino")
        subparser.add_argument("--project-root")
    return parser


def main(argv=None):
    parser = criar_parser()
    args = parser.parse_args(argv)
    if not args.modo:
        parser.print_help()
        return 0

    project_root = Path(args.project_root).resolve() if args.project_root else obter_root_projeto()
    if args.modo == "demo":
        acoes = montar_acoes_demo(args.destino)
    elif args.modo == "cliente":
        acoes = montar_acoes_cliente(args.destino)
    elif args.modo == "update":
        acoes = montar_acoes_update(args.destino)
    else:
        acoes = montar_acoes_verificar(project_root)

    return executar_acoes(acoes, confirmar=args.confirmar, dry_run=args.dry_run, project_root=project_root)


if __name__ == "__main__":
    raise SystemExit(main())
