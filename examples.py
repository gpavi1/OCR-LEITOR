"""
Exemplos de Uso - OCR LEITOR

Este arquivo demonstra como usar cada módulo do projeto
"""

# ============================================================================
# EXEMPLO 1: Usar como Menu Interativo
# ============================================================================

def exemplo_1_menu_interativo():
    """Menu interativo com todas as opções"""
    from src.main import OrquestradorAutomacao
    
    orq = OrquestradorAutomacao()
    # Automático - segue o menu interativo
    # python -m src.main


# ============================================================================
# EXEMPLO 2: Ler um Arquivo com OCR
# ============================================================================

def exemplo_2_ler_ocr():
    """Lê um arquivo e extrai texto via OCR"""
    from src.leitor import LeitorOCR
    
    leitor = LeitorOCR()
    
    # Ler imagem
    texto, sucesso = leitor.ler_imagem("entrada/nota.jpg")
    if sucesso:
        print(f"Texto extraído ({len(texto)} caracteres):")
        print(texto)
    
    # Ler PDF
    texto, sucesso = leitor.ler_pdf("entrada/nota.pdf")
    if sucesso:
        print(f"Texto extraído do PDF:")
        print(texto)


# ============================================================================
# EXEMPLO 3: Extrair Campos de Texto
# ============================================================================

def exemplo_3_extrair_campos():
    """Extrai campos estruturados do texto OCR"""
    from src.leitor import LeitorOCR
    from src.extrator import ExtratorCampos
    
    leitor = LeitorOCR()
    extrator = ExtratorCampos()
    
    # Ler arquivo
    texto, ok = leitor.ler_arquivo("entrada/nota.pdf")
    
    if ok:
        # Extrair campos
        campos = extrator.extrair_todos_campos(texto)
        
        print(f"Empresa: {campos['empresa']}")
        print(f"NF-e: {campos['nfe']}")
        print(f"Chave: {campos['chave']}")
        print(f"Vencimento: {campos['vencimento']}")
        
        # Validar
        validacao = extrator.validar_campos(campos)
        print(f"\nValidação:")
        for campo, valido in validacao.items():
            status = "✅" if valido else "❌"
            print(f"  {status} {campo}")


# ============================================================================
# EXEMPLO 4: Conferência Manual
# ============================================================================

def exemplo_4_conferencia():
    """Mostra a tela de conferência e aguarda confirmação"""
    from src.main import OrquestradorAutomacao
    
    orq = OrquestradorAutomacao()
    
    campos = {
        "empresa": "ABC LTDA",
        "nfe": "123456",
        "chave": "35250612345678000123550010001234567890123456",
        "vencimento": "15/07/2026"
    }
    
    # Solicitar confirmação (mostra a tela interativa)
    confirmado = orq._solicitar_confirmacao(campos)
    print(f"Confirmado: {confirmado}")


# ============================================================================
# EXEMPLO 5: Integração com Monday.com
# ============================================================================

def exemplo_5_monday_api():
    """Cria item no Monday e atualiza campos"""
    from src.monday_api import MondayAPI
    
    # Inicializar (substituir com credenciais reais)
    api = MondayAPI(
        api_key="seu_token_aqui",
        board_id="123456"
    )
    
    # Criar novo item
    item = api.criar_item("ABC LTDA - NF 123456", "ABC LTDA")
    if item:
        item_id = item["id"]
        print(f"Item criado: {item_id}")
        
        # Atualizar campos
        campos = {
            "empresa": "ABC LTDA",
            "nfe": "123456",
            "chave": "35250612345678000123550010001234567890123456",
            "vencimento": "15/07/2026"
        }
        
        api.atualizar_campos(item_id, campos)
        
        # Adicionar arquivo
        api.adicionar_arquivo(item_id, "entrada/nota.pdf")


# ============================================================================
# EXEMPLO 6: Processar um Arquivo Completo
# ============================================================================

def exemplo_6_processar_arquivo():
    """Processa um arquivo completo (todas as fases)"""
    from src.main import OrquestradorAutomacao
    
    orq = OrquestradorAutomacao()
    
    # Processar um arquivo
    sucesso, resultado = orq.processar_arquivo("entrada/nota.pdf")
    
    print(f"Sucesso: {sucesso}")
    print(f"Fase: {resultado['fase']}")
    print(f"Mensagem: {resultado['mensagem']}")
    print(f"Campos: {resultado['campos']}")


# ============================================================================
# EXEMPLO 7: Processamento em Lote
# ============================================================================

def exemplo_7_lote():
    """Processa todos os arquivos de uma pasta"""
    from src.main import OrquestradorAutomacao
    
    orq = OrquestradorAutomacao()
    
    # Processar lote
    resultados = orq.processar_lote("./entrada")
    
    print(f"Total: {resultados['total']}")
    print(f"Sucesso: {resultados['sucesso']}")
    print(f"Erro: {resultados['erro']}")
    
    # Ver detalhes
    for detalhe in resultados['detalhes']:
        print(f"\n{detalhe['arquivo']}: {detalhe['mensagem']}")


# ============================================================================
# EXEMPLO 8: Gerenciar Arquivos
# ============================================================================

def exemplo_8_gerenciador_arquivos():
    """Gerencia movimento de arquivos"""
    from src.uploader import Uploader
    
    uploader = Uploader()
    
    # Validar arquivo
    valido, msg = uploader.validar_arquivo("entrada/nota.pdf")
    print(f"Válido: {valido} - {msg}")
    
    # Mover para processadas
    sucesso, novo_caminho = uploader.mover_para_processadas("entrada/nota.pdf")
    if sucesso:
        print(f"Arquivo movido para: {novo_caminho}")
    
    # Mover para erro
    sucesso, novo_caminho = uploader.mover_para_erro("entrada/nota2.pdf", "OCR falhou")
    
    # Listar arquivos
    processados = uploader.listar_arquivos_processados()
    erros = uploader.listar_arquivos_erro()
    
    print(f"Processados: {len(processados)}")
    print(f"Com erro: {len(erros)}")


# ============================================================================
# EXEMPLO 9: Usar Configurações Customizadas
# ============================================================================

def exemplo_9_config_customizada():
    """Usa arquivo de configuração customizado"""
    from src.leitor import LeitorOCR
    from src.extrator import ExtratorCampos
    
    # Carregar com config customizada
    leitor = LeitorOCR(config_path="./config/settings.json")
    extrator = ExtratorCampos(config_path="./config/settings.json")
    
    # Agora usa as configurações do arquivo


# ============================================================================
# EXEMPLO 10: Logging e Debug
# ============================================================================

def exemplo_10_logging():
    """Exemplo com logging ativo"""
    import logging
    
    # Configurar logging detalhado
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    from src.main import OrquestradorAutomacao
    
    orq = OrquestradorAutomacao()
    
    # Agora todos os logs serão exibidos no console
    sucesso, resultado = orq.processar_arquivo("entrada/nota.pdf")


# ============================================================================
# EXEMPLO 11: Processamento Customizado
# ============================================================================

def exemplo_11_customizado():
    """Processamento customizado com lógica própria"""
    from src.leitor import LeitorOCR
    from src.extrator import ExtratorCampos
    from src.uploader import Uploader
    from pathlib import Path
    import json
    
    leitor = LeitorOCR()
    extrator = ExtratorCampos()
    uploader = Uploader()
    
    # Processar cada arquivo
    pasta_entrada = Path("./entrada")
    
    for arquivo in pasta_entrada.glob("*.pdf"):
        # Ler
        texto, ok = leitor.ler_arquivo(str(arquivo))
        
        if not ok:
            uploader.mover_para_erro(str(arquivo), "OCR failed")
            continue
        
        # Extrair
        campos = extrator.extrair_todos_campos(texto)
        
        # Fazer algo com os campos
        print(f"{arquivo.name}: {campos['empresa']}")
        
        # Salvar resultado em JSON
        com_json = arquivo.with_suffix('.json')
        with open(com_json, 'w', encoding='utf-8') as f:
            json.dump(campos, f, ensure_ascii=False, indent=2)


# ============================================================================
# EXEMPLO 12: Integração Customizada
# ============================================================================

def exemplo_12_integracao_customizada():
    """Integração com sistema externo customizado"""
    from src.leitor import LeitorOCR
    from src.extrator import ExtratorCampos
    
    leitor = LeitorOCR()
    extrator = ExtratorCampos()
    
    # Seu sistema customizado
    class MeuSistema:
        def registrar_nota(self, campos):
            """Registra nota em seu sistema"""
            print(f"Registrando no meu sistema: {campos}")
    
    sistema = MeuSistema()
    
    # Processar e integrar
    texto, ok = leitor.ler_arquivo("entrada/nota.pdf")
    if ok:
        campos = extrator.extrair_todos_campos(texto)
        validacao = extrator.validar_campos(campos)
        
        if all(validacao.values()):
            sistema.registrar_nota(campos)


if __name__ == "__main__":
    print("Exemplos de Uso - OCR LEITOR\n")
    print("Para usar um exemplo, descomente a linha correspondente:\n")
    
    exemplos = [
        ("1", "Menu Interativo", exemplo_1_menu_interativo),
        ("2", "Ler com OCR", exemplo_2_ler_ocr),
        ("3", "Extrair Campos", exemplo_3_extrair_campos),
        ("4", "Conferência Manual", exemplo_4_conferencia),
        ("5", "API Monday", exemplo_5_monday_api),
        ("6", "Processar Arquivo", exemplo_6_processar_arquivo),
        ("7", "Processamento em Lote", exemplo_7_lote),
        ("8", "Gerenciador de Arquivos", exemplo_8_gerenciador_arquivos),
        ("9", "Config Customizada", exemplo_9_config_customizada),
        ("10", "Logging e Debug", exemplo_10_logging),
        ("11", "Processamento Customizado", exemplo_11_customizado),
        ("12", "Integração Customizada", exemplo_12_integracao_customizada),
    ]
    
    for num, nome, func in exemplos:
        print(f"{num:2d}. {nome:.<40} exemplo_{num}_*")
    
    print("\nExemplo: python -c 'from examples import *; exemplo_2_ler_ocr()'")
