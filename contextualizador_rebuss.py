#!/usr/bin/env python3
"""Contextualizador para logs do sistema Rebuss"""

import re
from typing import Dict, List, Optional

class RebussContextualizer:
    """Contextualiza logs do sistema Rebuss baseado no reposit?rio"""
    
    def __init__(self):
        self.context_patterns = {
            "Counter": {
                "capturas": {
                    "perform_copy_from_reader": {
                        "description": "Processo de importa??o autom?tica de dados do leitor",
                        "context": "O usu?rio estava executando uma importa??o autom?tica de dados capturados por um leitor de c?digos de barras",
                        "typical_issues": ["Dados nulos vindos do leitor", "Formato de dados inesperado", "Problemas de conex?o com o leitor"]
                    }
                },
                "inventarios": {
                    "dashboard": {
                        "description": "Painel de controle do invent?rio",
                        "context": "O usu?rio estava acessando o painel principal do invent?rio para visualizar resumos e estat?sticas",
                        "typical_issues": ["Tabelas de cache n?o existem", "Problemas de performance em consultas grandes", "Dados corrompidos"]
                    }
                },
                "network_devices": {
                    "adopt_unifi_controller": {
                        "description": "Ado??o/configura??o de controlador Unifi",
                        "context": "O usu?rio estava tentando configurar ou adotar um controlador de rede Unifi",
                        "typical_issues": ["Loop infinito na configura??o", "Problemas de conectividade com o controlador", "Configura??es conflitantes"]
                    }
                }
            },
            "Admin": {
                "inventories": {
                    "destroy": {
                        "description": "Exclus?o de invent?rio",
                        "context": "O administrador estava tentando excluir um invent?rio do sistema",
                        "typical_issues": ["Invent?rio j? foi exclu?do", "Invent?rio tem depend?ncias", "Permiss?es insuficientes"]
                    }
                },
                "attendants": {
                    "index": {
                        "description": "Listagem de atendentes",
                        "context": "O administrador estava visualizando a lista de atendentes de um turno de trabalho",
                        "typical_issues": ["Turno de trabalho n?o existe", "Dados de atendentes corrompidos", "Problemas de relacionamento entre tabelas"]
                    }
                }
            }
        }
    
    def extract_context_from_log(self, log_entry: Dict) -> Dict:
        """Extrai contexto do log para contextualiza??o"""
        
        app = log_entry.get('app', 'UNKNOWN')
        url = log_entry.get('url', '')
        error_msg = log_entry.get('error_msg', '')
        request_params = log_entry.get('request_params', '')
        
        # Extrair controller e action da URL
        controller, action = self._extract_controller_action(url, request_params)
        
        # Buscar contexto espec?fico
        context_info = self._get_specific_context(app, controller, action, error_msg)
        
        return {
            "app": app,
            "controller": controller,
            "action": action,
            "context_info": context_info,
            "user_intent": self._determine_user_intent(app, controller, action),
            "error_context": self._analyze_error_context(error_msg, app, controller, action)
        }
    
    def _extract_controller_action(self, url: str, request_params: str) -> tuple:
        """Extrai controller e action da URL ou par?metros"""
        
        # Tentar extrair da URL primeiro
        if "/capturas/" in url:
            if "perform_copy_from_reader" in url:
                return "capturas", "perform_copy_from_reader"
        elif "/inventarios/" in url:
            if "dashboard" in url or url.endswith("/"):
                return "inventarios", "dashboard"
        elif "/inventories/" in url:
            return "inventories", "destroy"  # Baseado no log Admin
        elif "/attendants" in url:
            return "attendants", "index"
        
        # Tentar extrair dos par?metros
        if request_params:
            controller_match = re.search(r'"controller"=>"([^"]+)"', request_params)
            action_match = re.search(r'"action"=>"([^"]+)"', request_params)
            
            if controller_match and action_match:
                return controller_match.group(1), action_match.group(1)
        
        return "unknown", "unknown"
    
    def _get_specific_context(self, app: str, controller: str, action: str, error_msg: str) -> Dict:
        """Busca contexto espec?fico baseado no app, controller e action"""
        
        app_contexts = self.context_patterns.get(app, {})
        controller_contexts = app_contexts.get(controller, {})
        action_context = controller_contexts.get(action, {})
        
        if action_context:
            return {
                "description": action_context.get("description", "Opera??o n?o identificada"),
                "context": action_context.get("context", "Contexto n?o dispon?vel"),
                "typical_issues": action_context.get("typical_issues", [])
            }
        
        return {
            "description": "Opera??o n?o identificada",
            "context": "Contexto n?o dispon?vel para esta opera??o",
            "typical_issues": []
        }
    
    def _determine_user_intent(self, app: str, controller: str, action: str) -> str:
        """Determina a inten??o do usu?rio baseada na opera??o"""
        
        intent_map = {
            ("Counter", "capturas", "perform_copy_from_reader"): "Importar dados automaticamente do leitor de c?digos de barras",
            ("Counter", "inventarios", "dashboard"): "Visualizar resumo e estat?sticas do invent?rio",
            ("Counter", "network_devices", "adopt_unifi_controller"): "Configurar ou adotar um controlador de rede Unifi",
            ("Admin", "inventories", "destroy"): "Excluir um invent?rio do sistema administrativo",
            ("Admin", "attendants", "index"): "Visualizar lista de atendentes de um turno de trabalho"
        }
        
        return intent_map.get((app, controller, action), "Opera??o n?o identificada")
    
    def _analyze_error_context(self, error_msg: str, app: str, controller: str, action: str) -> str:
        """Analisa o contexto do erro espec?fico"""
        
        if not error_msg:
            return "Mensagem de erro n?o dispon?vel"
            
        if "undefined method" in error_msg.lower():
            return "O c?digo tentou chamar um m?todo em um objeto que est? vazio (nil). Isso geralmente acontece quando dados esperados n?o foram carregados ou processados corretamente."
        
        elif "couldn't find" in error_msg.lower() and "with 'id'" in error_msg.lower():
            return "O sistema tentou buscar um registro (invent?rio, turno, etc.) que n?o existe no banco de dados. Pode ter sido exclu?do ou nunca existiu."
        
        elif "relation" in error_msg.lower() and "does not exist" in error_msg.lower():
            return "O banco de dados est? tentando acessar uma tabela que n?o existe. Isso indica que migra??es n?o foram executadas ou h? problemas na estrutura do banco."
        
        elif "could not be found" in error_msg.lower():
            return "O sistema n?o conseguiu encontrar a a??o ou p?gina solicitada. Pode ser um problema de roteamento ou a funcionalidade n?o foi implementada."
        
        elif "stack level too deep" in error_msg.lower():
            return "Loop infinito detectado! O c?digo est? chamando a si mesmo recursivamente sem condi??o de parada. Isso causa estouro da pilha de execu??o (stack overflow)."
        
        return "Erro n?o identificado - an?lise manual necess?ria"
    
    def create_contextualization_block(self, log_entry: Dict) -> str:
        """Cria bloco de contextualiza??o"""
        
        context_data = self.extract_context_from_log(log_entry)
        
        block = f"""CONTEXTUALIZACAO
```
O que estava acontecendo:
{context_data['user_intent']}

Descricao da operacao:
{context_data['context_info']['description']}

Contexto detalhado:
{context_data['context_info']['context']}

Analise do erro:
{context_data['error_context']}
```"""
        
        return block

def test_contextualizer():
    """Testa o contextualizador"""
    
    print("=== TESTE CONTEXTUALIZADOR ===")
    
    # Log de exemplo Counter
    log_counter = {
        "app": "Counter",
        "url": "http://localhost/capturas/perform_copy_from_reader.json",
        "request_params": '{"importacion"=>"automatica", "controller"=>"capturas", "action"=>"perform_copy_from_reader", "format"=>"json"}',
        "error_msg": "undefined method `split' for nil:NilClass"
    }
    
    # Log de exemplo Admin
    log_admin = {
        "app": "Admin",
        "url": "https://admin.rebuss.com/inventories/41995",
        "request_params": '{"_method"=>"delete", "controller"=>"inventories", "action"=>"destroy", "id"=>"41995"}',
        "error_msg": "Couldn't find Inventory with 'id'=41995"
    }
    
    contextualizer = RebussContextualizer()
    
    # Testar Counter
    print("\n--- TESTE COUNTER ---")
    context_data_counter = contextualizer.extract_context_from_log(log_counter)
    print("DADOS DE CONTEXTO COUNTER:")
    for key, value in context_data_counter.items():
        print(f"  {key}: {value}")
    
    block_counter = contextualizer.create_contextualization_block(log_counter)
    print("\nBLOCO COUNTER CRIADO:")
    print(block_counter)
    
    # Testar Admin
    print("\n--- TESTE ADMIN ---")
    context_data_admin = contextualizer.extract_context_from_log(log_admin)
    print("DADOS DE CONTEXTO ADMIN:")
    for key, value in context_data_admin.items():
        print(f"  {key}: {value}")
    
    block_admin = contextualizer.create_contextualization_block(log_admin)
    print("\nBLOCO ADMIN CRIADO:")
    print(block_admin)

if __name__ == "__main__":
    test_contextualizer()
