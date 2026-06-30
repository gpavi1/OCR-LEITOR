import os
import shutil
import subprocess
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
PYTHON_VENV = BASE_DIR / ".venv" / "Scripts" / "python.exe"


def python_do_projeto():
    if PYTHON_VENV.is_file():
        return str(PYTHON_VENV)
    return "python"


def executar_comando(comando, cwd=None):
    try:
        resultado = subprocess.run(
            comando,
            cwd=cwd or str(BASE_DIR),
            shell=True,
            timeout=120,
        )
        return resultado.returncode
    except subprocess.TimeoutExpired:
        print("Comando excedeu o tempo limite.")
        return 1


def abrir_url(url):
    try:
        if sys.platform == "win32":
            os.startfile(url)
        else:
            import webbrowser
            webbrowser.open(url)
    except Exception as exc:
        print(f"Nao foi possivel abrir o navegador: {exc}")


def confirmar_frase(frase_esperada):
    print()
    print(f"ATENCAO: Esta operacao requer confirmacao.")
    print(f"Digite exatamente: {frase_esperada}")
    print("ou deixe em branco para cancelar.")
    resposta = input("> ").strip()
    return resposta == frase_esperada


def pausar():
    if sys.stdin.isatty():
        input("Pressione Enter para continuar...")


def limpar_tela():
    if sys.stdin.isatty():
        os.system("cls" if sys.platform == "win32" else "clear")


def opcao_verificar_ambiente():
    print()
    py = python_do_projeto()
    script = str(BASE_DIR / "scripts" / "doctor_instalacao.py")
    if not Path(script).is_file():
        print("Script doctor_instalacao.py nao encontrado.")
        print("Execute 'Validar Tesseract' e 'Validar MySQL' separadamente.")
        return
    executar_comando(f'"{py}" "{script}"')


def opcao_criar_venv():
    if PYTHON_VENV.is_file():
        print("Ambiente virtual .venv ja existe.")
        if not confirmar_frase("RECRIAR VENV"):
            print("Cancelado.")
            return
        import shutil
        shutil.rmtree(str(BASE_DIR / ".venv"), ignore_errors=True)
        print("Ambiente virtual removido.")

    print("Criando ambiente virtual...")
    code = executar_comando(f'python -m venv "{BASE_DIR / ".venv"}"')
    if code == 0:
        print("Ambiente virtual criado com sucesso.")
    else:
        print("Erro ao criar ambiente virtual.")


def opcao_instalar_requirements():
    py = python_do_projeto()
    print("Instalando requirements.txt...")
    code = executar_comando(f'"{py}" -m pip install -r "{BASE_DIR / "requirements.txt"}"')
    if code != 0:
        print("Erro ao instalar requirements.txt")
        return

    req_add = BASE_DIR / "requirements.add.txt"
    if req_add.is_file():
        print("Instalando requirements.add.txt...")
        code = executar_comando(f'"{py}" -m pip install -r "{req_add}"')
        if code != 0:
            print("Erro ao instalar requirements.add.txt")
            return

    print("Dependencias instaladas com sucesso.")


def opcao_validar_tesseract():
    py = python_do_projeto()
    script = str(BASE_DIR / "scripts" / "validador_tesseract.py")
    if not Path(script).is_file():
        print("Script validador_tesseract.py nao encontrado.")
        return
    executar_comando(f'"{py}" "{script}"')


def opcao_validar_mysql():
    py = python_do_projeto()
    script = str(BASE_DIR / "scripts" / "validador_mysql.py")
    if not Path(script).is_file():
        print("Script validador_mysql.py nao encontrado.")
        return
    executar_comando(f'"{py}" "{script}"')


def opcao_preparar_pastas():
    py = python_do_projeto()
    script = str(BASE_DIR / "scripts" / "preparar_instalacao_local.py")
    if not Path(script).is_file():
        print("Script preparar_instalacao_local.py nao encontrado.")
        return
    print("Preparando pastas operacionais (dry-run padrao)...")
    executar_comando(f'"{py}" "{script}"')


def opcao_configurar_ambiente():
    py = python_do_projeto()
    script = str(BASE_DIR / "scripts" / "configurar_ambiente.py")
    if not Path(script).is_file():
        print("Script configurar_ambiente.py nao encontrado.")
        return
    print("Abrindo configurador seguro de ambiente...")
    executar_comando(f'"{py}" "{script}"')


def opcao_iniciar_web():
    bat = str(BASE_DIR / "INICIAR_WEB_LOCAL.bat")
    if not Path(bat).is_file():
        print("INICIAR_WEB_LOCAL.bat nao encontrado.")
        return
    print("Abrindo painel web em nova janela...")
    subprocess.Popen(["cmd", "/c", "start", "OCR-LEITOR WEB", bat], shell=True)


def opcao_iniciar_ocr_24h():
    bat = str(BASE_DIR / "INICIAR_OCR_24H_LOCAL.bat")
    if not Path(bat).is_file():
        print("INICIAR_OCR_24H_LOCAL.bat nao encontrado.")
        return
    print("Abrindo OCR 24h em nova janela...")
    subprocess.Popen(["cmd", "/c", "start", "OCR-LEITOR OCR 24h", bat], shell=True)


def opcao_health():
    print("Abrindo health check no navegador...")
    abrir_url("http://127.0.0.1:5000/health")


def opcao_config_integracoes():
    print("Abrindo configuracao de integracoes no navegador...")
    abrir_url("http://127.0.0.1:5000/integracoes/configuracao")


def opcao_testes_rapidos():
    py = python_do_projeto()
    testes = [
        "tests/test_doctor_instalacao.py",
        "tests/test_preparar_instalacao_local.py",
        "tests/test_iniciar_web_local_bat.py",
        "tests/test_iniciar_ocr_24h_local_bat.py",
    ]
    for teste_rel in testes:
        teste = BASE_DIR / teste_rel
        if not teste.is_file():
            print(f"Aviso: {teste_rel} nao encontrado, pulando.")
            continue
        print(f"\n--- Rodando {teste_rel} ---")
        code = executar_comando(f'"{py}" -m pytest "{teste}" -v')
        if code != 0:
            print(f"Teste {teste_rel} falhou (codigo {code}).")


def opcao_testes_completos():
    py = python_do_projeto()
    print("Rodando suite completa de testes...")
    executar_comando(f'"{py}" -m pytest')


def opcao_limpar_ambiente():
    print()
    print("Esta operacao move arquivos operacionais para _backup_testes.")
    print("Banco, OCR, parser e API nao serao alterados.")
    if not confirmar_frase("LIMPAR TESTE"):
        print("Cancelado.")
        return

    bat = str(BASE_DIR / "8_LIMPAR_AMBIENTE_TESTE.bat")
    if not Path(bat).is_file():
        print("8_LIMPAR_AMBIENTE_TESTE.bat nao encontrado.")
        return
    executar_comando(f'"{bat}"')


def opcao_reset_banco():
    print()
    print("Esta operacao apaga registros de teste do banco MySQL.")
    print("Documentos e tentativas de integracao serao removidos.")
    print("Backup automatico e obrigatorio.")
    if not confirmar_frase("RESET TESTE"):
        print("Cancelado.")
        return

    bat = str(BASE_DIR / "9_RESET_BANCO_TESTE.bat")
    if not Path(bat).is_file():
        print("9_RESET_BANCO_TESTE.bat nao encontrado.")
        return
    executar_comando(f'"{bat}"')


def opcao_gerar_release():
    py = python_do_projeto()
    script = str(BASE_DIR / "scripts" / "gerar_release_limpa.py")
    if not Path(script).is_file():
        print("Script gerar_release_limpa.py nao encontrado.")
        return
    print("Gerando release limpa via git archive...")
    executar_comando(f'"{py}" "{script}" --confirmar')


OPCOES = [
    ("1", "Verificar ambiente", opcao_verificar_ambiente),
    ("2", "Criar .venv", opcao_criar_venv),
    ("3", "Instalar requirements", opcao_instalar_requirements),
    ("4", "Validar Tesseract", opcao_validar_tesseract),
    ("5", "Validar MySQL", opcao_validar_mysql),
    ("6", "Preparar pastas operacionais", opcao_preparar_pastas),
    ("7", "Configurar ambiente (Monday + Web + MySQL)", opcao_configurar_ambiente),
    ("8", "Iniciar painel web local", opcao_iniciar_web),
    ("9", "Iniciar OCR 24h local", opcao_iniciar_ocr_24h),
    ("10", "Abrir health local", opcao_health),
    ("11", "Abrir configuracao de integracoes", opcao_config_integracoes),
    ("12", "Rodar testes rapidos", opcao_testes_rapidos),
    ("13", "Rodar testes completos", opcao_testes_completos),
    ("14", "Limpar ambiente de teste", opcao_limpar_ambiente),
    ("15", "Reset banco de teste", opcao_reset_banco),
    ("16", "Gerar release limpa", opcao_gerar_release),
    ("17", "Sair", None),
]


def exibir_menu():
    limpar_tela()
    print("=" * 46)
    print("   OCR-LEITOR - Menu de Operacao Local")
    print("=" * 46)
    print()
    for chave, descricao, _ in OPCOES:
        print(f"  {chave}. {descricao}")
    print()
    print("-" * 46)
    print("  Nenhuma operacao altera dados reais sem")
    print("  confirmacao explicita.")
    print()


def menu():
    while True:
        exibir_menu()
        escolha = input("Escolha uma opcao: ").strip()
        print()

        for chave, descricao, funcao in OPCOES:
            if escolha == chave:
                if funcao is None:
                    print("Encerrando. Ate logo!")
                    return
                funcao()
                pausar()
                break
        else:
            print("Opcao invalida. Tente novamente.")
            pausar()


if __name__ == "__main__":
    try:
        menu()
    except KeyboardInterrupt:
        print("\nEncerrando. Ate logo!")
        sys.exit(0)
