"""
Módulo Uploader
Gerencia movimento e upload de arquivos após processamento
"""

import logging
import shutil
from pathlib import Path
from typing import Tuple
import os

logger = logging.getLogger(__name__)


class Uploader:
    """Classe para gerenciar arquivos processados"""
    
    def __init__(self, 
                 pasta_processadas: str = "./processadas",
                 pasta_erro: str = "./erro"):
        """
        Inicializa o uploader
        
        Args:
            pasta_processadas: Caminho da pasta de processados
            pasta_erro: Caminho da pasta de erros
        """
        self.pasta_processadas = Path(pasta_processadas)
        self.pasta_erro = Path(pasta_erro)
        
        # Criar pastas se não existirem
        self.pasta_processadas.mkdir(exist_ok=True)
        self.pasta_erro.mkdir(exist_ok=True)
        
        logger.info("Uploader inicializado")
    
    def mover_para_processadas(self, caminho_arquivo: str) -> Tuple[bool, str]:
        """
        Move arquivo para pasta de processadas
        
        Args:
            caminho_arquivo: Caminho do arquivo
            
        Returns:
            Tuple[bool, str]: (sucesso, novo_caminho)
        """
        try:
            caminho = Path(caminho_arquivo)
            
            if not caminho.exists():
                logger.error(f"Arquivo não encontrado: {caminho_arquivo}")
                return False, ""
            
            novo_caminho = self.pasta_processadas / caminho.name
            
            # Evitar sobrescrita
            if novo_caminho.exists():
                stem = novo_caminho.stem
                suffix = novo_caminho.suffix
                novo_caminho = self.pasta_processadas / f"{stem}_{Path.cwd().name}{suffix}"
            
            shutil.move(str(caminho), str(novo_caminho))
            logger.info(f"Arquivo movido para processadas: {novo_caminho}")
            
            return True, str(novo_caminho)
            
        except Exception as e:
            logger.error(f"Erro ao mover arquivo para processadas: {str(e)}")
            return False, ""
    
    def mover_para_erro(self, caminho_arquivo: str, motivo: str = "") -> Tuple[bool, str]:
        """
        Move arquivo para pasta de erros
        
        Args:
            caminho_arquivo: Caminho do arquivo
            motivo: Motivo do erro
            
        Returns:
            Tuple[bool, str]: (sucesso, novo_caminho)
        """
        try:
            caminho = Path(caminho_arquivo)
            
            if not caminho.exists():
                logger.error(f"Arquivo não encontrado: {caminho_arquivo}")
                return False, ""
            
            novo_caminho = self.pasta_erro / caminho.name
            
            # Evitar sobrescrita
            if novo_caminho.exists():
                stem = novo_caminho.stem
                suffix = novo_caminho.suffix
                novo_caminho = self.pasta_erro / f"{stem}_{Path.cwd().name}{suffix}"
            
            shutil.move(str(caminho), str(novo_caminho))
            
            if motivo:
                logger.warning(f"Arquivo movido para erro ({motivo}): {novo_caminho}")
            else:
                logger.warning(f"Arquivo movido para erro: {novo_caminho}")
            
            return True, str(novo_caminho)
            
        except Exception as e:
            logger.error(f"Erro ao mover arquivo para erro: {str(e)}")
            return False, ""
    
    def listar_arquivos_processados(self) -> list:
        """
        Lista todos os arquivos já processados
        
        Returns:
            Lista de caminhos dos arquivos
        """
        try:
            arquivos = list(self.pasta_processadas.glob("*"))
            logger.info(f"Total de arquivos processados: {len(arquivos)}")
            return [str(a) for a in arquivos]
        except Exception as e:
            logger.error(f"Erro ao listar arquivos processados: {str(e)}")
            return []
    
    def listar_arquivos_erro(self) -> list:
        """
        Lista todos os arquivos com erro
        
        Returns:
            Lista de caminhos dos arquivos
        """
        try:
            arquivos = list(self.pasta_erro.glob("*"))
            logger.info(f"Total de arquivos com erro: {len(arquivos)}")
            return [str(a) for a in arquivos]
        except Exception as e:
            logger.error(f"Erro ao listar arquivos com erro: {str(e)}")
            return []
    
    def obter_tamanho_arquivo(self, caminho_arquivo: str) -> int:
        """
        Obtém tamanho do arquivo em bytes
        
        Args:
            caminho_arquivo: Caminho do arquivo
            
        Returns:
            Tamanho em bytes
        """
        try:
            return Path(caminho_arquivo).stat().st_size
        except Exception as e:
            logger.error(f"Erro ao obter tamanho do arquivo: {str(e)}")
            return 0
    
    def validar_arquivo(self, caminho_arquivo: str, 
                       extensoes_permitidas: list = None) -> Tuple[bool, str]:
        """
        Valida se o arquivo é válido
        
        Args:
            caminho_arquivo: Caminho do arquivo
            extensoes_permitidas: Lista de extensões permitidas
            
        Returns:
            Tuple[bool, str]: (válido, mensagem)
        """
        try:
            caminho = Path(caminho_arquivo)
            
            # Verificar existência
            if not caminho.exists():
                return False, "Arquivo não encontrado"
            
            # Verificar tamanho (máximo 50MB)
            tamanho = self.obter_tamanho_arquivo(caminho_arquivo)
            if tamanho > 50 * 1024 * 1024:
                return False, "Arquivo maior que 50MB"
            
            # Verificar extensão
            if extensoes_permitidas:
                if caminho.suffix.lower() not in extensoes_permitidas:
                    return False, f"Extensão não permitida: {caminho.suffix}"
            
            return True, "OK"
            
        except Exception as e:
            return False, f"Erro na validação: {str(e)}"


# Exemplo de uso
if __name__ == "__main__":
    uploader = Uploader()
    
    # Listar processados
    # processados = uploader.listar_arquivos_processados()
    # print(f"Processados: {processados}")
    
    # Validar arquivo
    # valido, msg = uploader.validar_arquivo("caminho/arquivo.pdf")
    # print(f"Válido: {valido}, {msg}")
