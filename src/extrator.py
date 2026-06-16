"""
FASE 2: Extrator de Campos
Módulo para extrair campos específicos do texto bruto usando regex
"""

import re
import logging
from typing import Dict, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class ExtratorCampos:
    """Classe para extrair campos de nota fiscal do texto OCR"""
    
    def __init__(self, config_path: str = "./config/settings.json"):
        """
        Inicializa o extrator de campos
        
        Args:
            config_path: Caminho para arquivo de configuração
        """
        self.config = self._carregar_config(config_path)
        self.patterns = self.config.get("regex_patterns", {})
        logger.info("ExtratorCampos inicializado com sucesso")
    
    def _carregar_config(self, config_path: str) -> dict:
        """Carrega configurações do JSON"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Arquivo de config não encontrado: {config_path}")
            return {"regex_patterns": {}}
    
    def extrair_todos_campos(self, texto: str) -> Dict[str, str]:
        """
        Extrai todos os campos necessários do texto
        
        Args:
            texto: Texto bruto extraído pelo OCR
            
        Returns:
            Dict com campos: empresa, nfe, chave, vencimento
        """
        campos = {
            "empresa": self.extrair_empresa(texto),
            "nfe": self.extrair_nfe(texto),
            "chave": self.extrair_chave(texto),
            "vencimento": self.extrair_vencimento(texto)
        }
        
        logger.info(f"Campos extraídos: {campos}")
        return campos
    
    def extrair_empresa(self, texto: str) -> str:
        """
        Extrai o nome da empresa do texto
        
        Args:
            texto: Texto bruto
            
        Returns:
            Nome da empresa ou string vazia
        """
        try:
            # Procurar por padrões comuns
            patterns_empresa = [
                r"(?:Razão Social|RAZÃO SOCIAL|Empresa|EMPRESA)[\s:]*([A-Z][A-Z\s\-\.0-9]*)",
                r"(?:de\s|da\s|para\s)[A-Z][A-Z\s\-\.0-9]{5,50}(?:LTDA|S\.?A|ME|EPP)",
                r"^[A-Z][A-Z\s\-\.0-9]{5,50}(?:LTDA|S\.?A|ME|EPP).*$"
            ]
            
            for pattern in patterns_empresa:
                matches = re.finditer(pattern, texto, re.MULTILINE)
                for match in matches:
                    empresa = match.group(1) if match.lastindex else match.group(0)
                    empresa = empresa.strip()
                    if len(empresa) > 3 and len(empresa) < 100:
                        logger.info(f"Empresa extraída: {empresa}")
                        return empresa
            
            logger.warning("Não foi possível extrair empresa")
            return ""
            
        except Exception as e:
            logger.error(f"Erro ao extrair empresa: {str(e)}")
            return ""
    
    def extrair_nfe(self, texto: str) -> str:
        """
        Extrai o número da NF-e
        
        Args:
            texto: Texto bruto
            
        Returns:
            Número da NF-e ou string vazia
        """
        try:
            # Padrão: N ou Nº ou N° seguido de números
            pattern = r"N[º°o]\.?\s*(\d+)"
            match = re.search(pattern, texto)
            
            if match:
                nfe = match.group(1)
                logger.info(f"NF-e extraída: {nfe}")
                return nfe
            
            # Tenta padrão alternativo: número de 6 dígitos próximo a "Nota"
            pattern_alt = r"(?:Nota Fiscal|NF|NF-e|NF-e).*?(\d{6})"
            match = re.search(pattern_alt, texto, re.IGNORECASE)
            
            if match:
                nfe = match.group(1)
                logger.info(f"NF-e extraída (alternativo): {nfe}")
                return nfe
            
            logger.warning("Não foi possível extrair NF-e")
            return ""
            
        except Exception as e:
            logger.error(f"Erro ao extrair NF-e: {str(e)}")
            return ""
    
    def extrair_chave(self, texto: str) -> str:
        """
        Extrai a chave de acesso (44 dígitos)
        
        Args:
            texto: Texto bruto
            
        Returns:
            Chave de acesso ou string vazia
        """
        try:
            # Padrão: exatamente 44 dígitos
            pattern = r"(\d{44})"
            match = re.search(pattern, texto)
            
            if match:
                chave = match.group(1)
                logger.info(f"Chave extraída: {chave}")
                return chave
            
            logger.warning("Não foi possível extrair chave de acesso")
            return ""
            
        except Exception as e:
            logger.error(f"Erro ao extrair chave: {str(e)}")
            return ""
    
    def extrair_vencimento(self, texto: str) -> str:
        """
        Extrai a data de vencimento
        
        Args:
            texto: Texto bruto
            
        Returns:
            Data de vencimento no formato DD/MM/YYYY ou string vazia
        """
        try:
            # Procurar por padrão de data
            pattern = r"(?:Vencimento|VENCIMENTO|Vencendo em|Data de Vencimento)[\s:]*(\d{2}/\d{2}/\d{4})"
            match = re.search(pattern, texto, re.IGNORECASE)
            
            if match:
                data = match.group(1)
                # Validar se é uma data válida
                if self._validar_data(data):
                    logger.info(f"Data de vencimento extraída: {data}")
                    return data
            
            # Padrão alternativo: qualquer data no formato DD/MM/YYYY
            pattern_alt = r"(\d{2}/\d{2}/\d{4})"
            matches = re.finditer(pattern_alt, texto)
            
            for match in matches:
                data = match.group(1)
                if self._validar_data(data):
                    logger.info(f"Data extraída (alternativo): {data}")
                    return data
            
            logger.warning("Não foi possível extrair data de vencimento")
            return ""
            
        except Exception as e:
            logger.error(f"Erro ao extrair vencimento: {str(e)}")
            return ""
    
    def _validar_data(self, data: str) -> bool:
        """
        Valida se a data está no formato correto DD/MM/YYYY
        
        Args:
            data: String com data
            
        Returns:
            True se válida, False caso contrário
        """
        try:
            dia, mes, ano = data.split('/')
            dia = int(dia)
            mes = int(mes)
            ano = int(ano)
            
            # Verificar se está no intervalo válido
            if mes < 1 or mes > 12:
                return False
            
            if dia < 1 or dia > 31:
                return False
            
            # Validar ano (deve ser futuro)
            if ano < 2020 or ano > 2100:
                return False
            
            return True
        except:
            return False
    
    def validar_campos(self, campos: Dict[str, str]) -> Dict[str, bool]:
        """
        Valida se todos os campos foram extraídos corretamente
        
        Args:
            campos: Dicionário com campos extraídos
            
        Returns:
            Dicionário com status de validação de cada campo
        """
        validacao = {
            "empresa": len(campos.get("empresa", "")) > 3,
            "nfe": len(campos.get("nfe", "")) > 0,
            "chave": len(campos.get("chave", "")) == 44,
            "vencimento": self._validar_data(campos.get("vencimento", ""))
        }
        
        logger.info(f"Validação de campos: {validacao}")
        return validacao


# Exemplo de uso
if __name__ == "__main__":
    extrator = ExtratorCampos()
    
    texto_exemplo = """
    Nota Fiscal Eletrônica
    Razão Social: ABC LTDA
    CNPJ: 12.345.678/0001-90
    Nº 123456
    Chave de Acesso: 35250612345678000123550010001234567890123456
    Data de Emissão: 15/06/2026
    Vencimento: 15/07/2026
    """
    
    campos = extrator.extrair_todos_campos(texto_exemplo)
    print(f"Campos extraídos: {campos}")
    
    validacao = extrator.validar_campos(campos)
    print(f"Validação: {validacao}")
