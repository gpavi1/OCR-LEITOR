import argparse
import getpass
import secrets
from datetime import datetime
from pathlib import Path
from shutil import copy2


VARIAVEIS = [
    {"chave": "WEB_SECRET_KEY", "grupo": "Web", "sensivel": True, "auto": True},
    {"chave": "WEB_USERNAME", "grupo": "Web", "sensivel": False, "padrao": "admin"},
    {"chave": "WEB_PASSWORD", "grupo": "Web", "sensivel": True},
    {"chave": "DB_HOST", "grupo": "MySQL", "sensivel": False, "padrao": "localhost"},
    {"chave": "DB_PORT", "grupo": "MySQL", "sensivel": False, "padrao": "3306"},
    {"chave": "DB_NAME", "grupo": "MySQL", "sensivel": False, "padrao": "ocr_leitor"},
    {"chave": "DB_USER", "grupo": "MySQL", "sensivel": False, "padrao": "ocr_app"},
    {"chave": "DB_PASSWORD", "grupo": "MySQL", "sensivel": True},
    {"chave": "MONDAY_API_TOKEN", "grupo": "Monday", "sensivel": True},
    {"chave": "MONDAY_BOARD_ID", "grupo": "Monday", "sensivel": False},
    {"chave": "MONDAY_COLUMN_EMPRESA", "grupo": "Monday", "sensivel": False},
    {"chave": "MONDAY_COLUMN_NUMERO_NF", "grupo": "Monday", "sensivel": False},
    {"chave": "MONDAY_COLUMN_CHAVE_ACESSO", "grupo": "Monday", "sensivel": False},
    {"chave": "MONDAY_COLUMN_VENCIMENTO", "grupo": "Monday", "sensivel": False},
    {"chave": "MONDAY_COLUMN_VALOR_TOTAL", "grupo": "Monday", "sensivel": False},
    {"chave": "MONDAY_COLUMN_OBSERVACAO", "grupo": "Monday", "sensivel": False},
]

CHAVES_CONHECIDAS = [item["chave"] for item in VARIAVEIS]
CHAVES_SENSIVEIS = {item["chave"] for item in VARIAVEIS if item.get("sensivel")}
TERMOS_PLACEHOLDER = (
    "placeholder",
    "trocar",
    "coloque",
    "seu_token",
    "sua_senha",
    "changeme",
    "example",
    "exemplo",
    "your_",
    "cole_",
    "cole ",
)


def obter_root_projeto():
    return Path(__file__).resolve().parents[1]


def carregar_env(caminho_env):
    caminho = Path(caminho_env)
    dados = {}
    if not caminho.exists():
        return dados

    for linha in caminho.read_text(encoding="utf-8").splitlines():
        texto = linha.strip()
        if not texto or texto.startswith("#") or "=" not in texto:
            continue
        chave, valor = texto.split("=", 1)
        dados[chave.strip()] = valor.strip()
    return dados


def salvar_env(caminho_env, dados):
    caminho = Path(caminho_env)
    caminho.parent.mkdir(parents=True, exist_ok=True)

    linhas = [
        "# Web",
        f"WEB_SECRET_KEY={dados.get('WEB_SECRET_KEY', '')}",
        f"WEB_USERNAME={dados.get('WEB_USERNAME', '')}",
        f"WEB_PASSWORD={dados.get('WEB_PASSWORD', '')}",
        "",
        "# MySQL",
        f"DB_HOST={dados.get('DB_HOST', '')}",
        f"DB_PORT={dados.get('DB_PORT', '')}",
        f"DB_NAME={dados.get('DB_NAME', '')}",
        f"DB_USER={dados.get('DB_USER', '')}",
        f"DB_PASSWORD={dados.get('DB_PASSWORD', '')}",
        "",
        "# Monday",
        f"MONDAY_API_TOKEN={dados.get('MONDAY_API_TOKEN', '')}",
        f"MONDAY_BOARD_ID={dados.get('MONDAY_BOARD_ID', '')}",
        f"MONDAY_COLUMN_EMPRESA={dados.get('MONDAY_COLUMN_EMPRESA', '')}",
        f"MONDAY_COLUMN_NUMERO_NF={dados.get('MONDAY_COLUMN_NUMERO_NF', '')}",
        f"MONDAY_COLUMN_CHAVE_ACESSO={dados.get('MONDAY_COLUMN_CHAVE_ACESSO', '')}",
        f"MONDAY_COLUMN_VENCIMENTO={dados.get('MONDAY_COLUMN_VENCIMENTO', '')}",
        f"MONDAY_COLUMN_VALOR_TOTAL={dados.get('MONDAY_COLUMN_VALOR_TOTAL', '')}",
        f"MONDAY_COLUMN_OBSERVACAO={dados.get('MONDAY_COLUMN_OBSERVACAO', '')}",
    ]

    extras = sorted(chave for chave in dados if chave not in CHAVES_CONHECIDAS)
    if extras:
        linhas.extend(["", "# Outras variaveis preservadas"])
        for chave in extras:
            linhas.append(f"{chave}={dados.get(chave, '')}")

    caminho.write_text("\n".join(linhas) + "\n", encoding="utf-8")


def criar_backup_env(caminho_env):
    caminho = Path(caminho_env)
    if not caminho.exists():
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = caminho.with_name(f"{caminho.name}.backup_{timestamp}")
    contador = 1
    while backup.exists():
        backup = caminho.with_name(f"{caminho.name}.backup_{timestamp}_{contador}")
        contador += 1
    copy2(caminho, backup)
    return backup


def eh_placeholder(valor):
    if valor is None:
        return True
    texto = str(valor).strip()
    if not texto:
        return True
    texto_lower = texto.lower()
    return any(termo in texto_lower for termo in TERMOS_PLACEHOLDER)


def mascarar_valor(chave, valor):
    if chave not in CHAVES_SENSIVEIS:
        return valor or ""
    texto = str(valor or "")
    if not texto:
        return ""
    if chave == "MONDAY_API_TOKEN" and len(texto) >= 4:
        return f"***{texto[-4:]}"
    return "********"


def gerar_web_secret_key():
    return secrets.token_urlsafe(32)


def _perguntar_valor(chave, valor_atual, padrao, sensivel, input_func, getpass_func):
    sufixo = f" [{padrao}]" if padrao else ""
    if sensivel:
        valor = getpass_func(f"{chave}{sufixo}: ").strip()
    else:
        valor = input_func(f"{chave}{sufixo}: ").strip()
    if not valor and padrao:
        return padrao
    if not valor and valor_atual and not eh_placeholder(valor_atual):
        return valor_atual
    return valor


def montar_configuracao_interativa(
    dados_existentes,
    input_func=None,
    getpass_func=None,
    interativo=True,
):
    input_func = input_func or input
    getpass_func = getpass_func or getpass.getpass
    dados = dict(dados_existentes or {})

    for item in VARIAVEIS:
        chave = item["chave"]
        atual = dados.get(chave, "")
        padrao = item.get("padrao", "")
        sensivel = bool(item.get("sensivel"))

        if chave == "WEB_SECRET_KEY" and eh_placeholder(atual):
            dados[chave] = gerar_web_secret_key()
            continue

        if atual and not eh_placeholder(atual):
            if not interativo:
                continue
            exibido = mascarar_valor(chave, atual)
            manter = input_func(f"Manter {chave} atual ({exibido})? [S/n]: ").strip().lower()
            if manter in ("", "s", "sim", "y", "yes"):
                continue

        if not interativo:
            if not atual and padrao:
                dados[chave] = padrao
            continue

        dados[chave] = _perguntar_valor(
            chave, atual, padrao, sensivel, input_func, getpass_func
        )

    return dados


def validar_configuracao(dados):
    bloqueios = []
    for item in VARIAVEIS:
        chave = item["chave"]
        valor = (dados or {}).get(chave, "")
        if eh_placeholder(valor):
            bloqueios.append(f"{chave} ausente ou placeholder.")
    return bloqueios


def gerar_resumo_configuracao(dados):
    linhas = []
    grupo_atual = None
    for item in VARIAVEIS:
        grupo = item["grupo"]
        if grupo != grupo_atual:
            if linhas:
                linhas.append("")
            linhas.append(f"# {grupo}")
            grupo_atual = grupo
        chave = item["chave"]
        linhas.append(f"{chave}={mascarar_valor(chave, (dados or {}).get(chave, ''))}")
    return "\n".join(linhas)


def imprimir_checklist(dados, bloqueios):
    print("\nChecklist final")
    print("=" * 16)
    print(gerar_resumo_configuracao(dados))
    if bloqueios:
        print("\nBloqueios:")
        for bloqueio in bloqueios:
            print(f"- {bloqueio}")
    else:
        print("\nConfiguracao completa.")
    print("\nReinicie o painel web para aplicar as alteracoes.")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Configurador seguro de ambiente do OCR-LEITOR"
    )
    parser.add_argument("--env-path", default=None, help="Caminho do arquivo .env")
    parser.add_argument("--dry-run", action="store_true", help="Simula sem gravar arquivo")
    parser.add_argument("--confirmar", action="store_true", help="Grava o .env apos montar a configuracao")
    args = parser.parse_args(argv)

    root = obter_root_projeto()
    env_path = Path(args.env_path) if args.env_path else root / ".env"
    dados_existentes = carregar_env(env_path)
    dados = montar_configuracao_interativa(dados_existentes, interativo=not args.dry_run)
    bloqueios = validar_configuracao(dados)

    imprimir_checklist(dados, bloqueios)

    if args.dry_run:
        print("\nDRY-RUN: nenhum arquivo foi gravado.")
        return 0

    if not args.confirmar:
        print("\nNada foi gravado. Execute novamente com --confirmar para salvar o .env.")
        return 0

    backup = criar_backup_env(env_path)
    salvar_env(env_path, dados)
    if backup:
        print(f"\nBackup criado: {backup}")
    print(f"Arquivo gravado: {env_path}")
    return 0 if not bloqueios else 1


if __name__ == "__main__":
    raise SystemExit(main())
