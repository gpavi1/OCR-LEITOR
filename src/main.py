"""
AUTOMAÇÃO PRINCIPAL - OCR LEITOR
Orquestra todas as fases de processamento
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Tuple
from datetime import datetime

# Importar módulos locais
from src.leitor import LeitorOCR
from src.extrator import ExtratorCampos
from src.monday_api import MondayAPI
from src.uploader import Uploader


# Configurar logging
def configurar_logging(pasta_logs: str = "./logs"):
    """Configura o logging da aplicação"""
    Path(pasta_logs).mkdir(exist_ok=True)
    
    log_file = Path(pasta_logs) / f"automacao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)


logger = configurar_logging()


class OrquestradorAutomacao:
    """Classe principal que orquestra todo o fluxo"""
    
    def __init__(self, config_path: str = "./config/settings.json"):
        """
        Inicializa o orquestrador
        
        Args:
            config_path: Caminho para arquivo de configuração
        """
        self.config = self._carregar_config(config_path)
        
        # Inicializar componentes
        self.leitor = LeitorOCR(config_path)
        self.extrator = ExtratorCampos(config_path)
        self.uploader = Uploader(
            pasta_processadas=self.config.get("pasta_processadas", "./processadas"),
            pasta_erro=self.config.get("pasta_erro", "./erro")
        )
        
        # Inicializar Monday apenas se credenciais estiverem configuradas
        self.monday = None
        if self._validar_credenciais_monday():
            self.monday = MondayAPI(
                api_key=self.config.get("monday_api_key"),
                board_id=self.config.get("monday_board_id"),
                config_path=config_path
            )
        
        self.pasta_entrada = self.config.get("pasta_entrada", "./entrada")
        logger.info("Orquestrador inicializado com sucesso")
    
    def _carregar_config(self, config_path: str) -> dict:
        """Carrega configurações"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Arquivo de config não encontrado: {config_path}")
            return {}
    
    def _validar_credenciais_monday(self) -> bool:
        """Valida se as credenciais do Monday estão configuradas"""
        api_key = self.config.get("monday_api_key", "").strip()
        board_id = self.config.get("monday_board_id", "").strip()
        
        if api_key == "YOUR_MONDAY_API_KEY_HERE" or board_id == "YOUR_BOARD_ID_HERE":
            logger.warning("Credenciais do Monday não configuradas. Modo offline.")
            return False
        
        if not api_key or not board_id:
            logger.warning("Credenciais do Monday incompletas. Modo offline.")
            return False
        
        return True
    
    def processar_arquivo(self, caminho_arquivo: str) -> Tuple[bool, Dict]:
        """
        Processa um arquivo completo
        
        FASE 1: Leitura OCR
        FASE 2: Extração de campos
        FASE 3: Conferência manual
        FASE 4: Envio para Monday
        FASE 5: Processamento em lote
        
        Args:
            caminho_arquivo: Caminho do arquivo
            
        Returns:
            Tuple[bool, Dict]: (sucesso, resultado)
        """
        resultado = {
            "arquivo": caminho_arquivo,
            "sucesso": False,
            "fase": 0,
            "texto": "",
            "campos": {},
            "mensagem": ""
        }
        
        try:
            # FASE 1: Validar arquivo
            resultado["fase"] = 1
            logger.info(f"[FASE 1] Validando arquivo: {caminho_arquivo}")
            
            valido, msg = self.uploader.validar_arquivo(
                caminho_arquivo,
                extensoes_permitidas=self.config.get("extensoes_suportadas")
            )
            
            if not valido:
                logger.error(f"Arquivo inválido: {msg}")
                self.uploader.mover_para_erro(caminho_arquivo, f"Validação: {msg}")
                resultado["mensagem"] = msg
                return False, resultado
            
            # FASE 1: Ler arquivo com OCR
            logger.info(f"[FASE 1] Lendo arquivo com OCR")
            texto, sucesso = self.leitor.ler_arquivo(caminho_arquivo)
            
            if not sucesso or not texto.strip():
                logger.error("Falha ao extrair texto com OCR")
                self.uploader.mover_para_erro(caminho_arquivo, "OCR falhou")
                resultado["mensagem"] = "Não foi possível extrair texto do arquivo"
                return False, resultado
            
            resultado["texto"] = texto
            
            # FASE 2: Extrair campos
            resultado["fase"] = 2
            logger.info(f"[FASE 2] Extraindo campos")
            campos = self.extrator.extrair_todos_campos(texto)
            resultado["campos"] = campos
            
            # Validar campos
            validacao = self.extrator.validar_campos(campos)
            campos_completos = all(validacao.values())
            
            if not campos_completos:
                logger.warning(f"Alguns campos não foram extraídos: {validacao}")
                logger.warning(f"Campos extraídos: {campos}")
            
            # FASE 3: Conferência manual
            resultado["fase"] = 3
            logger.info(f"[FASE 3] Apresentando dados para conferência")
            
            if self.config.get("confirmacao_manual", True):
                confirmado = self._solicitar_confirmacao(campos)
                if not confirmado:
                    logger.info("Usuário cancelou o envio")
                    self.uploader.mover_para_erro(caminho_arquivo, "Cancelado pelo usuário")
                    resultado["mensagem"] = "Processamento cancelado pelo usuário"
                    return False, resultado
            
            # FASE 4: Integração Monday
            resultado["fase"] = 4
            logger.info(f"[FASE 4] Integração Monday")
            
            if self.monday:
                # Criar item
                nome_item = f"{campos.get('empresa', 'SEM EMPRESA')} - NF {campos.get('nfe', '?')}"
                item = self.monday.criar_item(nome_item, campos.get("empresa", ""))
                
                if item:
                    item_id = item.get("id")
                    logger.info(f"Item criado no Monday: {item_id}")
                    
                    # Atualizar campos
                    self.monday.atualizar_campos(item_id, campos)
                    
                    # Adicionar arquivo
                    self.monday.adicionar_arquivo(item_id, caminho_arquivo)
                else:
                    logger.warning("Falha ao criar item no Monday")
            else:
                logger.info("Monday não configurado - modo offline")
            
            # FASE 5: Mover para processadas
            resultado["fase"] = 5
            logger.info(f"[FASE 5] Finalizando processamento")
            
            sucesso_mover, novo_caminho = self.uploader.mover_para_processadas(caminho_arquivo)
            
            if sucesso_mover:
                logger.info(f"Arquivo processado com sucesso: {novo_caminho}")
                resultado["sucesso"] = True
                resultado["mensagem"] = "Processado com sucesso"
                return True, resultado
            else:
                logger.error("Falha ao mover arquivo para processadas")
                resultado["mensagem"] = "Falha ao finalizar processamento"
                return False, resultado
            
        except Exception as e:
            logger.error(f"Erro durante processamento: {str(e)}")
            resultado["mensagem"] = f"Erro: {str(e)}"
            
            # Mover para erro
            self.uploader.mover_para_erro(caminho_arquivo, str(e))
            
            return False, resultado
    
    def processar_lote(self, pasta: str = None) -> Dict:
        """
        Processa todos os arquivos de uma pasta
        
        Args:
            pasta: Pasta a processar (padrão: pasta_entrada)
            
        Returns:
            Dicionário com estatísticas
        """
        if pasta is None:
            pasta = self.pasta_entrada
        
        logger.info(f"Iniciando processamento em lote da pasta: {pasta}")
        
        pasta_path = Path(pasta)
        if not pasta_path.exists():
            logger.error(f"Pasta não encontrada: {pasta}")
            return {"error": "Pasta não encontrada"}
        
        # Listar arquivos suportados
        extensoes = self.config.get("extensoes_suportadas", [".jpg", ".jpeg", ".png", ".pdf"])
        arquivos = []
        
        for ext in extensoes:
            arquivos.extend(pasta_path.glob(f"*{ext}"))
            arquivos.extend(pasta_path.glob(f"*{ext.upper()}"))
        
        logger.info(f"Total de arquivos encontrados: {len(arquivos)}")
        
        # Processar cada arquivo
        resultados = {
            "total": len(arquivos),
            "sucesso": 0,
            "erro": 0,
            "detalhes": []
        }
        
        for i, arquivo in enumerate(arquivos, 1):
            logger.info(f"\n{'='*60}")
            logger.info(f"Processando arquivo {i}/{len(arquivos)}")
            logger.info(f"{'='*60}\n")
            
            sucesso, resultado = self.processar_arquivo(str(arquivo))
            
            if sucesso:
                resultados["sucesso"] += 1
            else:
                resultados["erro"] += 1
            
            resultados["detalhes"].append(resultado)
        
        # Resumo final
        logger.info(f"\n{'='*60}")
        logger.info("RESUMO DO PROCESSAMENTO")
        logger.info(f"{'='*60}")
        logger.info(f"Total processados: {resultados['sucesso']}/{resultados['total']}")
        logger.info(f"Com erro: {resultados['erro']}/{resultados['total']}")
        
        return resultados
    
    def _solicitar_confirmacao(self, campos: Dict) -> bool:
        """
        Exibe os dados e solicita confirmação do usuário
        
        Args:
            campos: Dicionário com campos extraídos
            
        Returns:
            True se confirmado, False caso contrário
        """
        print("\n" + "="*60)
        print("CONFERÊNCIA DE DADOS - VERIFIQUE SE ESTÁ CORRETO")
        print("="*60)
        print(f"\nEMPRESA:\n{campos.get('empresa', '[NÃO EXTRAÍDO]')}")
        print(f"\nNF-E:\n{campos.get('nfe', '[NÃO EXTRAÍDO]')}")
        print(f"\nCHAVE DE ACESSO:\n{campos.get('chave', '[NÃO EXTRAÍDO]')}")
        print(f"\nVENCIMENTO:\n{campos.get('vencimento', '[NÃO EXTRAÍDO]')}")
        print("\n" + "="*60)
        
        while True:
            resposta = input("\nConfirmar envio para Monday? [S/N]: ").strip().upper()
            
            if resposta == "S":
                print("✓ Confirmado. Processando...\n")
                return True
            elif resposta == "N":
                print("✗ Cancelado pelo usuário.\n")
                return False
            else:
                print("Opção inválida. Digite S para sim ou N para não.")


def main():
    """Função principal"""
    try:
        # Criar orquestrador
        orq = OrquestradorAutomacao()
        
        # Menu de opções
        print("\n" + "="*60)
        print("OCR LEITOR - AUTOMAÇÃO DE NOTAS FISCAIS")
        print("="*60)
        print("\nOpções:")
        print("1. Processar arquivo específico")
        print("2. Processar todos os arquivos da pasta entrada")
        print("3. Ver estatísticas")
        print("4. Sair")
        print("\n" + "="*60)
        
        opcao = input("\nEscolha uma opção [1-4]: ").strip()
        
        if opcao == "1":
            caminho = input("Digite o caminho do arquivo: ").strip()
            sucesso, resultado = orq.processar_arquivo(caminho)
            print(f"\nResultado: {resultado}")
        
        elif opcao == "2":
            resultados = orq.processar_lote()
            print(f"\nResultados: {resultados}")
        
        elif opcao == "3":
            processados = orq.uploader.listar_arquivos_processados()
            erros = orq.uploader.listar_arquivos_erro()
            print(f"\nArquivos processados: {len(processados)}")
            print(f"Arquivos com erro: {len(erros)}")
        
        elif opcao == "4":
            print("Saindo...")
            sys.exit(0)
        
        else:
            print("Opção inválida")
    
    except KeyboardInterrupt:
        logger.info("Automação interrompida pelo usuário")
        print("\nAutomação interrompida.")
    
    except Exception as e:
        logger.error(f"Erro fatal: {str(e)}")
        print(f"Erro: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
