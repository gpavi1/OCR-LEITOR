"""
FASE 4: Integração Monday
Módulo para criar itens e atualizar colunas no Monday.com via GraphQL
"""

import requests
import logging
import json
from typing import Dict, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)


class MondayAPI:
    """Classe para integração com Monday.com via GraphQL"""
    
    API_URL = "https://api.monday.com/v2"
    
    def __init__(self, api_key: str, board_id: str, config_path: str = "./config/settings.json"):
        """
        Inicializa a integração Monday
        
        Args:
            api_key: Chave de API do Monday
            board_id: ID do board
            config_path: Caminho para arquivo de configuração
        """
        self.api_key = api_key
        self.board_id = board_id
        self.config = self._carregar_config(config_path)
        self.colunas = self.config.get("colunas_monday", {})
        self.headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json"
        }
        logger.info(f"MondayAPI inicializado - Board: {board_id}")
    
    def _carregar_config(self, config_path: str) -> dict:
        """Carrega configurações do JSON"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Arquivo de config não encontrado: {config_path}")
            return {"colunas_monday": {}}
    
    def criar_item(self, nome_item: str, empresa: str) -> Optional[Dict]:
        """
        Cria um novo item no board
        
        Args:
            nome_item: Nome do item (geralmente empresa + NF)
            empresa: Empresa do item
            
        Returns:
            Resposta da API ou None se falhar
        """
        try:
            logger.info(f"Criando item: {nome_item}")
            
            query = """
            mutation {
                create_item(
                    board_id: %s,
                    item_name: "%s",
                    column_values: "{}") {
                    id
                    name
                }
            }
            """ % (self.board_id, nome_item.replace('"', '\\"'))
            
            response = self._executar_query(query)
            
            if response and "data" in response:
                item_id = response["data"]["create_item"]["id"]
                logger.info(f"Item criado com ID: {item_id}")
                return response["data"]["create_item"]
            else:
                logger.error(f"Erro ao criar item: {response}")
                return None
                
        except Exception as e:
            logger.error(f"Erro na criação do item: {str(e)}")
            return None
    
    def atualizar_campos(self, item_id: str, campos: Dict[str, str]) -> bool:
        """
        Atualiza os campos do item no Monday
        
        Args:
            item_id: ID do item
            campos: Dicionário com valores: {empresa, nfe, chave, vencimento}
            
        Returns:
            True se sucesso, False caso contrário
        """
        try:
            logger.info(f"Atualizando campos do item {item_id}")
            
            # Construir valores de coluna
            column_values = self._construir_column_values(campos)
            
            query = """
            mutation {
                change_multiple_column_values(
                    item_id: "%s",
                    board_id: %s,
                    column_values: "%s") {
                    id
                }
            }
            """ % (item_id, self.board_id, column_values.replace('"', '\\"'))
            
            response = self._executar_query(query)
            
            if response and "data" in response:
                logger.info(f"Campos atualizados para item {item_id}")
                return True
            else:
                logger.error(f"Erro ao atualizar campos: {response}")
                return False
                
        except Exception as e:
            logger.error(f"Erro na atualização dos campos: {str(e)}")
            return False
    
    def adicionar_arquivo(self, item_id: str, caminho_arquivo: str) -> bool:
        """
        Adiciona um arquivo ao item
        
        Args:
            item_id: ID do item
            caminho_arquivo: Caminho local do arquivo
            
        Returns:
            True se sucesso, False caso contrário
        """
        try:
            logger.info(f"Adicionando arquivo {caminho_arquivo} ao item {item_id}")
            
            caminho = Path(caminho_arquivo)
            if not caminho.exists():
                logger.error(f"Arquivo não encontrado: {caminho_arquivo}")
                return False
            
            # Obter o ID da coluna de upload
            coluna_upload_id = self._obter_coluna_upload()
            if not coluna_upload_id:
                logger.error("Coluna de upload não encontrada")
                return False
            
            # Preparar arquivo para upload
            with open(caminho_arquivo, 'rb') as f:
                files = {'file': f}
                
                query = """
                mutation {
                    add_file_to_column(
                        item_id: "%s",
                        column_id: "%s",
                        file: "%s") {
                        id
                    }
                }
                """ % (item_id, coluna_upload_id, caminho.name)
                
                response = self._executar_query(query, files=files)
                
                if response and "data" in response:
                    logger.info(f"Arquivo adicionado ao item {item_id}")
                    return True
                else:
                    logger.error(f"Erro ao adicionar arquivo: {response}")
                    return False
            
        except Exception as e:
            logger.error(f"Erro ao adicionar arquivo: {str(e)}")
            return False
    
    def _construir_column_values(self, campos: Dict[str, str]) -> str:
        """
        Constrói JSON com valores de coluna para Monday
        
        Args:
            campos: Dicionário com valores
            
        Returns:
            String JSON com column_values
        """
        # Mapear campos locais para colunas do Monday
        column_mapping = {
            "empresa": self.colunas.get("empresa", "Elemento"),
            "nfe": self.colunas.get("nfe", "NUMERO NF-E"),
            "chave": self.colunas.get("chave", "CH.ACESSO"),
            "vencimento": self.colunas.get("vencimento", "VENCIMENTO")
        }
        
        # Construir JSON
        column_values = {}
        for campo, valor in campos.items():
            coluna = column_mapping.get(campo)
            if coluna and valor:
                # Remover espaços e caracteres especiais do nome da coluna
                coluna_id = coluna.replace(" ", "_").replace(".", "").lower()
                column_values[coluna_id] = {"text": valor}
        
        return json.dumps(column_values)
    
    def _obter_coluna_upload(self) -> Optional[str]:
        """
        Obtém o ID da coluna de upload no board
        
        Returns:
            ID da coluna ou None
        """
        try:
            query = """
            query {
                boards(ids: %s) {
                    columns {
                        id
                        title
                    }
                }
            }
            """ % self.board_id
            
            response = self._executar_query(query)
            
            if response and "data" in response:
                columns = response["data"]["boards"][0]["columns"]
                for col in columns:
                    if "upload" in col["title"].lower() or "arquivo" in col["title"].lower():
                        return col["id"]
            
            logger.warning("Coluna de upload não encontrada")
            return None
            
        except Exception as e:
            logger.error(f"Erro ao obter coluna de upload: {str(e)}")
            return None
    
    def _executar_query(self, query: str, files: Optional[Dict] = None) -> Optional[Dict]:
        """
        Executa uma query GraphQL no Monday
        
        Args:
            query: Query GraphQL
            files: Arquivos para upload (opcional)
            
        Returns:
            Resposta da API em JSON ou None
        """
        try:
            payload = {"query": query}
            
            response = requests.post(
                self.API_URL,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            
            response.raise_for_status()
            
            data = response.json()
            
            if "errors" in data:
                logger.error(f"Erro GraphQL: {data['errors']}")
                return None
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Erro ao executar query: {str(e)}")
            return None
    
    def obter_items(self) -> Optional[List[Dict]]:
        """
        Obtém lista de items do board
        
        Returns:
            Lista de items ou None
        """
        try:
            query = """
            query {
                boards(ids: %s) {
                    items {
                        id
                        name
                    }
                }
            }
            """ % self.board_id
            
            response = self._executar_query(query)
            
            if response and "data" in response:
                items = response["data"]["boards"][0]["items"]
                logger.info(f"Total de items: {len(items)}")
                return items
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao obter items: {str(e)}")
            return None


# Exemplo de uso
if __name__ == "__main__":
    # Testar integração (substituir com valores reais)
    api = MondayAPI(api_key="YOUR_API_KEY", board_id="YOUR_BOARD_ID")
    
    # Criar item
    # item = api.criar_item("ABC LTDA - NF 123456", "ABC LTDA")
    
    # Atualizar campos
    # campos = {
    #     "empresa": "ABC LTDA",
    #     "nfe": "123456",
    #     "chave": "35250612345678000123550010001234567890123456",
    #     "vencimento": "15/07/2026"
    # }
    # api.atualizar_campos("item_id", campos)
    
    # Adicionar arquivo
    # api.adicionar_arquivo("item_id", "caminho/arquivo.pdf")
