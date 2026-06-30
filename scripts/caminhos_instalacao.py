from pathlib import Path


CAMINHO_PADRAO_CLIENTE = r"C:\OCR-LEITOR"
CAMINHO_PADRAO_DEMO = r"C:\OCR-LEITOR-DEMO"
NOME_MARCADOR_INSTALACAO = ".ocr_leitor_install.json"

PASTAS_OPERACIONAIS = ["input", "output", "processed", "erro", "logs", "exports"]
PASTAS_RECOMENDADAS = [
    "input",
    "output",
    "processed",
    "erro",
    "logs",
    "exports",
    "backups",
    "config",
    "database",
    "web",
    "scripts",
    "conectores",
    "services",
]


def normalizar_caminho(caminho):
    return str(Path(caminho).expanduser())


def _partes_normalizadas(caminho):
    return [parte.lower() for parte in Path(normalizar_caminho(caminho)).parts]


def _caminho_normalizado_lower(caminho):
    return normalizar_caminho(caminho).lower()


def esta_em_onedrive(caminho):
    return any("onedrive" in parte for parte in _partes_normalizadas(caminho))


def esta_em_desktop(caminho):
    partes = _partes_normalizadas(caminho)
    return any(parte in {"desktop", "area de trabalho", "área de trabalho"} for parte in partes)


def esta_em_downloads(caminho):
    return any(parte == "downloads" for parte in _partes_normalizadas(caminho))


def esta_em_temp(caminho):
    partes = _partes_normalizadas(caminho)
    return any(parte in {"temp", "tmp"} for parte in partes)


def esta_em_repositorio_git_externo(caminho):
    path = Path(caminho).expanduser().absolute()
    for parent in path.parents:
        if (parent / ".git").exists():
            return True
    return False


def detectar_instalacao_existente(caminho):
    base = Path(caminho).expanduser()
    sinais = []

    arquivos_sinalizadores = [
        ".env",
        "OCR-LEITOR.cmd",
        str(Path("web") / "app.py"),
        str(Path("database") / "schema.sql"),
        NOME_MARCADOR_INSTALACAO,
    ]
    for relativo in arquivos_sinalizadores:
        if (base / relativo).exists():
            sinais.append(relativo)

    for pasta in PASTAS_OPERACIONAIS:
        if (base / pasta).is_dir():
            sinais.append(pasta)

    marcador_encontrado = NOME_MARCADOR_INSTALACAO in sinais
    sinais_fortes = [
        sinal
        for sinal in sinais
        if sinal in {".env", "OCR-LEITOR.cmd", str(Path("web") / "app.py"), str(Path("database") / "schema.sql")}
    ]
    pastas_operacionais = [sinal for sinal in sinais if sinal in PASTAS_OPERACIONAIS]
    existe = marcador_encontrado or len(sinais_fortes) >= 2 or len(pastas_operacionais) == len(PASTAS_OPERACIONAIS)

    return {
        "existe": existe,
        "sinais": sinais,
        "marcador_encontrado": marcador_encontrado,
    }


def obter_estrutura_pastas_recomendada(modo="cliente"):
    return list(PASTAS_RECOMENDADAS)


def _avisos_caminho_inseguro(caminho):
    avisos = []
    if esta_em_onedrive(caminho):
        avisos.append("Caminho dentro de OneDrive.")
    if esta_em_desktop(caminho):
        avisos.append("Caminho dentro de Desktop/Area de Trabalho.")
    if esta_em_downloads(caminho):
        avisos.append("Caminho dentro de Downloads.")
    if esta_em_temp(caminho):
        avisos.append("Caminho dentro de Temp.")
    if esta_em_repositorio_git_externo(caminho):
        avisos.append("Caminho dentro de outro repositorio Git.")
    return avisos


def classificar_caminho_instalacao(caminho, modo="cliente"):
    modo_normalizado = (modo or "cliente").lower().strip()
    if modo_normalizado not in {"cliente", "demo", "update", "desenvolvimento"}:
        modo_normalizado = "cliente"

    caminho_normalizado = normalizar_caminho(caminho)
    caminho_lower = _caminho_normalizado_lower(caminho)
    cliente_lower = CAMINHO_PADRAO_CLIENTE.lower()
    demo_lower = CAMINHO_PADRAO_DEMO.lower()
    avisos = []
    bloqueios = []

    avisos_inseguros = _avisos_caminho_inseguro(caminho)
    if modo_normalizado == "desenvolvimento":
        avisos.extend(avisos_inseguros)
    elif modo_normalizado == "demo":
        avisos.extend(avisos_inseguros)
    else:
        bloqueios.extend(avisos_inseguros)

    if modo_normalizado == "cliente":
        recomendacao = f"Para cliente, use {CAMINHO_PADRAO_CLIENTE}. Para demo, use {CAMINHO_PADRAO_DEMO}."
        if caminho_lower == demo_lower:
            bloqueios.append("Caminho reservado para demo.")
    elif modo_normalizado == "demo":
        recomendacao = f"Para demo, use {CAMINHO_PADRAO_DEMO}."
        if caminho_lower == cliente_lower:
            avisos.append("Caminho de cliente real usado em modo demo.")
    elif modo_normalizado == "update":
        recomendacao = f"Update deve rodar sobre uma instalacao existente em {CAMINHO_PADRAO_CLIENTE}."
        instalacao = detectar_instalacao_existente(caminho)
        if not instalacao["existe"]:
            bloqueios.append("Update exige instalação existente.")
    else:
        recomendacao = f"Modo desenvolvimento apenas alerta. Cliente: {CAMINHO_PADRAO_CLIENTE}. Demo: {CAMINHO_PADRAO_DEMO}."

    return {
        "caminho": caminho_normalizado,
        "modo": modo_normalizado,
        "seguro": not bloqueios,
        "bloqueios": bloqueios,
        "avisos": avisos,
        "recomendacao": recomendacao,
    }
