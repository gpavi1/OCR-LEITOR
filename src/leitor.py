"""
FASE 1: Leitor OCR
Módulo para ler imagens e PDFs e extrair texto usando Tesseract OCR
"""

import cv2
import pytesseract
import logging
from pathlib import Path
from typing import Union, Tuple
from pdf2image import convert_from_path
from PIL import Image
import json

logger = logging.getLogger(__name__)


class LeitorOCR:
    """Classe para leitura de imagens e PDFs com OCR"""
    
    def __init__(self, config_path: str = "./config/settings.json"):
        """
        Inicializa o leitor OCR
        
        Args:
            config_path: Caminho para arquivo de configuração
        """
        self.config = self._carregar_config(config_path)
        self._configurar_tesseract()
        logger.info("LeitorOCR inicializado com sucesso")
    
    def _carregar_config(self, config_path: str) -> dict:
        """Carrega configurações do JSON"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Arquivo de config não encontrado: {config_path}")
            return {"tesseract_path": "tesseract"}
    
    def _configurar_tesseract(self):
        """Configura caminho do Tesseract"""
        tesseract_path = self.config.get("tesseract_path")
        if tesseract_path and Path(tesseract_path).exists():
            pytesseract.pytesseract.pytesseract_cmd = tesseract_path
            logger.info(f"Tesseract configurado em: {tesseract_path}")
        else:
            logger.warning("Caminho do Tesseract não encontrado, usando padrão do sistema")
    
    def ler_imagem(self, caminho_arquivo: str) -> Tuple[str, bool]:
        """
        Lê uma imagem e extrai texto via OCR
        
        Args:
            caminho_arquivo: Caminho da imagem
            
        Returns:
            Tuple[str, bool]: (texto extraído, sucesso)
        """
        try:
            logger.info(f"Lendo imagem: {caminho_arquivo}")
            
            # Ler imagem com OpenCV
            imagem = cv2.imread(caminho_arquivo)
            if imagem is None:
                logger.error(f"Não foi possível ler a imagem: {caminho_arquivo}")
                return "", False
            
            # Pré-processamento para melhorar OCR
            imagem = self._preprocessar_imagem(imagem)
            
            # Converter BGR para RGB para pytesseract
            imagem_rgb = cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB)
            
            # Extrair texto
            texto = pytesseract.image_to_string(imagem_rgb, lang='por')
            
            if texto.strip():
                logger.info(f"Texto extraído com sucesso ({len(texto)} caracteres)")
                return texto, True
            else:
                logger.warning("Nenhum texto foi extraído da imagem")
                return "", False
                
        except Exception as e:
            logger.error(f"Erro ao ler imagem: {str(e)}")
            return "", False
    
    def ler_pdf(self, caminho_arquivo: str) -> Tuple[str, bool]:
        """
        Lê um PDF e extrai texto via OCR
        
        Args:
            caminho_arquivo: Caminho do PDF
            
        Returns:
            Tuple[str, bool]: (texto extraído, sucesso)
        """
        try:
            logger.info(f"Lendo PDF: {caminho_arquivo}")
            
            # Converter PDF em imagens
            paginas = convert_from_path(caminho_arquivo, dpi=300)
            
            if not paginas:
                logger.error(f"PDF vazio ou não pode ser convertido: {caminho_arquivo}")
                return "", False
            
            texto_completo = ""
            
            # Processar cada página
            for i, pagina in enumerate(paginas):
                logger.info(f"Processando página {i + 1}/{len(paginas)}")
                
                # Converter PIL para OpenCV
                imagem_cv = cv2.cvtColor(
                    cv2.UMat.get(cv2.UMat(cv2.imread(str(Path(caminho_arquivo))))).__array__(),
                    cv2.COLOR_BGR2RGB
                )
                
                # Melhor forma: converter PIL para array numpy
                import numpy as np
                imagem_array = np.array(pagina)
                
                # Pré-processar
                imagem_array = self._preprocessar_imagem_pillow(imagem_array)
                
                # Extrair texto
                texto_pagina = pytesseract.image_to_string(imagem_array, lang='por')
                texto_completo += texto_pagina + "\n"
            
            if texto_completo.strip():
                logger.info(f"Texto extraído do PDF com sucesso ({len(texto_completo)} caracteres)")
                return texto_completo, True
            else:
                logger.warning("Nenhum texto foi extraído do PDF")
                return "", False
                
        except Exception as e:
            logger.error(f"Erro ao ler PDF: {str(e)}")
            return "", False
    
    def ler_arquivo(self, caminho_arquivo: str) -> Tuple[str, bool]:
        """
        Lê um arquivo (imagem ou PDF) automaticamente
        
        Args:
            caminho_arquivo: Caminho do arquivo
            
        Returns:
            Tuple[str, bool]: (texto extraído, sucesso)
        """
        extensao = Path(caminho_arquivo).suffix.lower()
        
        if extensao == ".pdf":
            return self.ler_pdf(caminho_arquivo)
        elif extensao in [".jpg", ".jpeg", ".png", ".gif", ".bmp"]:
            return self.ler_imagem(caminho_arquivo)
        else:
            logger.error(f"Extensão não suportada: {extensao}")
            return "", False
    
    def _preprocessar_imagem(self, imagem):
        """Pré-processa imagem para melhorar OCR"""
        # Converter para escala de cinza
        imagem_cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
        
        # Aplicar threshold binário
        _, imagem_binaria = cv2.threshold(imagem_cinza, 150, 255, cv2.THRESH_BINARY)
        
        # Remover ruído
        imagem_limpa = cv2.medianBlur(imagem_binaria, 3)
        
        return imagem_limpa
    
    def _preprocessar_imagem_pillow(self, imagem):
        """Pré-processa imagem PIL para melhorar OCR"""
        import numpy as np
        
        # Converter para escala de cinza
        imagem_cinza = np.array(Image.fromarray(imagem).convert('L'))
        
        # Aplicar threshold binário
        _, imagem_binaria = cv2.threshold(imagem_cinza, 150, 255, cv2.THRESH_BINARY)
        
        return imagem_binaria


# Exemplo de uso
if __name__ == "__main__":
    leitor = LeitorOCR()
    
    # Testar com uma imagem
    # texto, sucesso = leitor.ler_imagem("caminho/da/imagem.jpg")
    # if sucesso:
    #     print(texto)
