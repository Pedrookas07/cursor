#!/usr/bin/env python3
"""Sistema Final Integrado - Vigil?ncia em Tempo Real com Formato Correto"""

import os
import time
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from parser_rebuss_simples import parse_rebuss_log_simples
from contextualizador_rebuss import RebussContextualizer

load_dotenv()

class SistemaFinalIntegrado:
    """Sistema final integrado com formato correto"""
    
    def __init__(self):
        self.bot_token = os.getenv('SLACK_BOT_TOKEN')
        self.read_channel = "G459BR2E9"  # Canal #desarrollo
        self.response_channel = "C09HX1HPFPB"  # Canal #monitor-inventarios
        self.last_message_ts = None
        self.running = False
        self.contextualizer = RebussContextualizer()
        
    def get_latest_messages(self):
        """Busca as mensagens mais recentes do canal #desarrollo"""
        
        url = "https://slack.com/api/conversations.history"
        headers = {
            "Authorization": f"Bearer {self.bot_token}",
            "Content-Type": "application/json"
        }
        
        params = {
            "channel": self.read_channel,
            "limit": 5,
            "inclusive": False
        }
        
        if self.last_message_ts:
            params["oldest"] = self.last_message_ts
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("ok"):
                messages = result.get("messages", [])
                
                if messages:
                    latest_ts = float(messages[0].get("ts", 0))
                    if self.last_message_ts is None or latest_ts > self.last_message_ts:
                        self.last_message_ts = latest_ts
                    
                    return messages
                else:
                    return []
            else:
                print(f"ERROR: {result.get('error')}")
                return []
                
        except Exception as e:
            print(f"ERROR: {e}")
            return []
    
    def is_log_message(self, message):
        """Verifica se a mensagem ? um log de erro"""
        
        text = message.get("text", "")
        
        log_indicators = [
            "error",
            "counter error",
            "admin error",
            "undefined method",
            "could not be found",
            "relation",
            "does not exist"
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in log_indicators)
    
    def create_inventory_info_block_final(self, log_entry):
        """Cria bloco com informa??es do invent?rio no formato final"""
        
        app = log_entry.get('app', 'UNKNOWN')
        error = log_entry.get('error', 'UNKNOWN')
        inventory_id = log_entry.get('inventory_id', 'N/A')
        inventory_name = log_entry.get('inventory_name', 'N/A')
        user = log_entry.get('user', 'N/A')
        url = log_entry.get('url', 'N/A')
        location = log_entry.get('location', 'N/A')
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Criar bloco baseado no tipo de app
        if app == "Admin":
            # Para Admin, n?o h? invent?rio espec?fico
            block = f"""SISTEMA E LOG
```
{timestamp} | {inventory_name} ({location})
{user} | {location}
{app} Error {error}
{url}
```"""
        else:
            # Para Counter, usar hyperlink do invent?rio
            inventory_link = f"<https://admin.rebuss.com/inventories/{inventory_id}/|{inventory_id} - {inventory_name}>"
            block = f"""INVENTARIO E LOG
```
{timestamp} | {inventory_link} ({location})
{user} | {location}
{app} Error {error}
{url}
```"""
        
        return block
    
    def create_statistics_block_final(self, log_entry):
        """Cria bloco com estat?sticas"""
        
        app = log_entry.get('app', 'UNKNOWN')
        error = log_entry.get('error', 'UNKNOWN')
        inventory_name = log_entry.get('inventory_name', 'N/A')
        
        severity = "CRITICA" if error == "500" else "MEDIA"
        impact = "Alto" if error == "500" else "Medio"
        error_type = "Erro de servidor" if error == "500" else "Erro de roteamento"
        
        # Buscar estat?sticas de frequ?ncia
        try:
            error_stats = self.get_error_statistics(log_entry)
            print(f"DEBUG: error_stats obtido: {error_stats}")
        except Exception as e:
            print(f"ERROR: Erro ao obter estat?sticas: {e}")
            import traceback
            traceback.print_exc()
            error_stats = {
                "total_similar_errors": "N/A",
                "inventory_specific_errors": "N/A",
                "period_days": 7
            }
        
        # Ajustar exibi??o baseado no tipo de app
        if app == "Admin":
            inventory_line = f"? Sistema: {inventory_name[:30]}{'...' if len(inventory_name) > 30 else ''}"
            frequency_line = f"? Frequencia (7 dias): {error_stats['total_similar_errors']} vezes no total"
            specific_line = ""  # Admin n?o precisa de linha espec?fica
        else:
            inventory_line = f"? Inventario: {inventory_name[:30]}{'...' if len(inventory_name) > 30 else ''}"
            frequency_line = f"? Frequencia (7 dias): {error_stats['total_similar_errors']} vezes no total"
            specific_line = f"? Este inventario: {error_stats['inventory_specific_errors']} vezes"
        
        block = f"""ESTATISTICAS
```
? App: {app}
? Severidade: {severity}
? Tipo: {error_type}
? Impacto: {impact}
{inventory_line}
{frequency_line}
{specific_line}
```"""
        
        return block
    
    def create_analysis_block_final(self, log_entry):
        """Cria bloco com an?lise espec?fica"""
        
        error_msg = log_entry.get('error_msg', '')
        app = log_entry.get('app', 'UNKNOWN')
        request_params = log_entry.get('request_params', '')
        
        if not error_msg:
            error_msg = "Mensagem de erro nao disponivel"
            
        if "undefined method" in error_msg.lower():
            error_type = "Metodo chamado em objeto nil"
        elif "could not be found" in error_msg.lower():
            error_type = "Action nao encontrada no controller"
        elif "relation" in error_msg.lower() and "does not exist" in error_msg.lower():
            error_type = "Tabela nao existe no banco de dados"
        elif "stack level too deep" in error_msg.lower():
            error_type = "Loop infinito (stack overflow)"
        else:
            error_type = "Erro nao identificado"
        
        # Mostrar par?metros da requisi??o se dispon?veis
        params_info = ""
        if request_params:
            params_info = f"\nParametros da requisicao:\n{request_params}"
        
        block = f"""ANALISE ESPECIFICA
```
Tipo: {error_type}
App: {app}
Descricao: {error_msg[:100]}{'...' if len(error_msg) > 100 else ''}{params_info}
```"""
        
        return block
    
    def create_solutions_block_final(self, log_entry):
        """Cria bloco com sugest?es de solu??es"""
        
        error_msg = log_entry.get('error_msg', '')
        
        if not error_msg:
            error_msg = "Mensagem de erro nao disponivel"
            
        if "undefined method" in error_msg.lower():
            solutions = [
                "Verificar se o objeto nao e nil antes de chamar metodos",
                "Usar safe navigation operator (&.)",
                "Adicionar verificacao de nil com try",
                "Verificar inicializacao do objeto"
            ]
            code_examples = [
                "# Safe navigation",
                "object&.method_name",
                "",
                "# Com try", 
                "object.try(:method_name)",
                "",
                "# Verificacao explicita",
                "if object.present?",
                "  object.method_name",
                "end"
            ]
        elif "could not be found" in error_msg.lower():
            solutions = [
                "Verificar se a action existe no controller",
                "Verificar rotas em config/routes.rb",
                "Verificar se o controller esta sendo carregado",
                "Verificar namespace e modulos do controller"
            ]
            code_examples = [
                "# Verificar action no controller",
                "class SettingsController < ApplicationController",
                "  def show",
                "    # implementacao da action",
                "  end",
                "end"
            ]
        elif "relation" in error_msg.lower() and "does not exist" in error_msg.lower():
            solutions = [
                "Executar migracoes pendentes: rails db:migrate",
                "Verificar se a tabela existe no banco",
                "Verificar se o modelo esta correto",
                "Verificar se as migracoes foram aplicadas"
            ]
            code_examples = [
                "# Verificar migracoes",
                "rails db:migrate:status",
                "",
                "# Executar migracoes pendentes", 
                "rails db:migrate"
            ]
        elif "stack level too deep" in error_msg.lower():
            solutions = [
                "Identificar o loop infinito no codigo (metodos se chamando mutuamente)",
                "Adicionar condicao de parada na recursao",
                "Verificar chamadas circulares entre metodos",
                "Implementar timeout ou limite de tentativas",
                "Revisar logica de reconexao do controlador Unifi"
            ]
            code_examples = [
                "# Adicionar condicao de parada",
                "def upload_router_config(attempts = 0)",
                "  return if attempts > 3  # Limite de tentativas",
                "  # ... logica ...",
                "end",
                "",
                "# Usar flag para evitar loops",
                "@configuring = false",
                "def check_router_configuration",
                "  return if @configuring",
                "  @configuring = true",
                "  # ... logica ...",
                "  @configuring = false",
                "end"
            ]
        else:
            solutions = ["Investigar manualmente o erro", "Verificar logs do servidor"]
            code_examples = ["# Investigacao manual necessaria"]
        
        solutions_text = ""
        for i, solution in enumerate(solutions, 1):
            solutions_text += f"{i}. {solution}\n"
        
        code_text = "\n".join(code_examples)
        
        block = f"""SUGESTOES DE SOLUCOES
```
{solutions_text.strip()}
```

EXEMPLO DE CODIGO
```ruby
{code_text}
```"""
        
        return block
    
    def get_error_statistics(self, log_entry):
        """Busca estat?sticas de frequ?ncia do erro no canal #desarrollo"""
        
        url = "https://slack.com/api/conversations.history"
        headers = {
            "Authorization": f"Bearer {self.bot_token}",
            "Content-Type": "application/json"
        }
        
        # Buscar mensagens dos ?ltimos 7 dias
        from datetime import datetime, timedelta
        seven_days_ago = datetime.now() - timedelta(days=7)
        oldest_ts = seven_days_ago.timestamp()
        
        params = {
            "channel": self.read_channel,
            "limit": 1000,  # M?ximo de mensagens
            "oldest": oldest_ts
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("ok"):
                messages = result.get("messages", [])
                
                # Contar erros similares
                app = log_entry.get('app', 'UNKNOWN')
                error_code = log_entry.get('error', 'UNKNOWN')
                inventory_id = log_entry.get('inventory_id', 'N/A')
                error_msg = log_entry.get('error_msg', '')
                
                total_similar_errors = 0
                inventory_specific_errors = 0
                
                for message in messages:
                    text = message.get("text", "")
                    
                    # Verificar se ? um erro similar
                    if f"{app} error {error_code}" in text:
                        total_similar_errors += 1
                        
                        # Para Counter, verificar invent?rio espec?fico
                        # Para Admin, n?o h? invent?rio espec?fico
                        if app == "Counter" and inventory_id and inventory_id != 'N/A' and str(inventory_id) in text:
                            inventory_specific_errors += 1
                        elif app == "Admin":
                            # Para Admin, n?o contamos invent?rio espec?fico
                            inventory_specific_errors = "N/A (Admin)"
                
                return {
                    "total_similar_errors": total_similar_errors,
                    "inventory_specific_errors": inventory_specific_errors,
                    "period_days": 7
                }
            else:
                return {
                    "total_similar_errors": "N/A",
                    "inventory_specific_errors": "N/A",
                    "period_days": 7
                }
                
        except Exception as e:
            print(f"ERROR ao buscar estat?sticas: {e}")
            return {
                "total_similar_errors": "N/A",
                "inventory_specific_errors": "N/A",
                "period_days": 7
            }
    
    def create_organized_alert_final(self, log_entry):
        """Cria alerta organizado em blocos - formato final"""
        
        app = log_entry.get('app', 'UNKNOWN')
        error = log_entry.get('error', 'UNKNOWN')
        
        header = f"ALERTA CRITICO REBUSS - {app.upper()} ERROR {error}"
        
        try:
            inventory_block = self.create_inventory_info_block_final(log_entry)
            print("DEBUG: inventory_block criado")
        except Exception as e:
            print(f"ERROR: Erro ao criar inventory_block: {e}")
            inventory_block = "ERRO: N?o foi poss?vel criar bloco de invent?rio"
        
        try:
            stats_block = self.create_statistics_block_final(log_entry)
            print("DEBUG: stats_block criado")
        except Exception as e:
            print(f"ERROR: Erro ao criar stats_block: {e}")
            stats_block = "ERRO: N?o foi poss?vel criar bloco de estat?sticas"
        
        try:
            context_block = self.contextualizer.create_contextualization_block(log_entry)
            print("DEBUG: context_block criado")
        except Exception as e:
            print(f"ERROR: Erro ao criar context_block: {e}")
            import traceback
            traceback.print_exc()
            context_block = "ERRO: N?o foi poss?vel criar bloco de contexto"
        
        try:
            analysis_block = self.create_analysis_block_final(log_entry)
            print("DEBUG: analysis_block criado")
        except Exception as e:
            print(f"ERROR: Erro ao criar analysis_block: {e}")
            analysis_block = "ERRO: N?o foi poss?vel criar bloco de an?lise"
        
        try:
            solutions_block = self.create_solutions_block_final(log_entry)
            print("DEBUG: solutions_block criado")
        except Exception as e:
            print(f"ERROR: Erro ao criar solutions_block: {e}")
            solutions_block = "ERRO: N?o foi poss?vel criar bloco de solu??es"
        
        organized_alert = f"""{header}

{inventory_block}

{stats_block}

{context_block}

{analysis_block}

{solutions_block}

---
Analise gerada pelo Sistema de Vigilancia Rebuss - {datetime.now().strftime('%d/%m/%Y %H:%M')}"""
        
        return organized_alert
    
    def send_organized_alert_final(self, log_entry):
        """Envia alerta organizado em blocos"""
        
        print(f"Criando alerta organizado para: {log_entry.get('error_msg', 'N/A')}")
        
        try:
            organized_alert = self.create_organized_alert_final(log_entry)
            print("DEBUG: organized_alert criado com sucesso")
        except Exception as e:
            print(f"ERROR: Erro ao criar organized_alert: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        payload = {
            "channel": self.response_channel,
            "text": organized_alert,
            "username": "Vigilante Inventarios",
            "icon_emoji": ":robot_face:"
        }
        
        headers = {
            "Authorization": f"Bearer {self.bot_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                "https://slack.com/api/chat.postMessage",
                json=payload,
                headers=headers
            )
            
            if response.json().get("ok"):
                print("SUCCESS: Alerta organizado enviado")
                return True
            else:
                print(f"ERROR: {response.json().get('error')}")
                return False
                
        except Exception as e:
            print(f"ERROR: {e}")
            return False
    
    def process_new_messages(self):
        """Processa novas mensagens e envia alertas"""
        
        messages = self.get_latest_messages()
        
        if not messages:
            return
        
        log_messages = [msg for msg in messages if self.is_log_message(msg)]
        
        if not log_messages:
            return
        
        print(f"{len(log_messages)} novas mensagens de log encontradas")
        
        for message in log_messages:
            print(f"DEBUG: Processando mensagem: {message.get('text', '')[:100]}...")
            
            parsed_data = parse_rebuss_log_simples(message.get("text", ""))
            print(f"DEBUG: Parsed data: {parsed_data}")
            
            if parsed_data is None:
                print("ERROR: parsed_data is None")
                continue
                
            # Adicionar informa??es do Slack
            print("DEBUG: Adicionando informa??es do Slack")
            try:
                parsed_data["timestamp"] = datetime.fromtimestamp(float(message.get("ts", 0))).isoformat()
                print("DEBUG: timestamp adicionado")
                parsed_data["channel"] = self.read_channel
                print("DEBUG: channel adicionado")
                parsed_data["raw_message"] = message
                print("DEBUG: raw_message adicionado")
            except Exception as e:
                print(f"ERROR: Erro ao adicionar informa??es do Slack: {e}")
                import traceback
                traceback.print_exc()
                continue
            
            error_msg = parsed_data.get('error_msg', 'N/A')
            if error_msg is None:
                error_msg = 'N/A'
            print(f"Processando log: {parsed_data.get('app', 'UNKNOWN')} - {error_msg[:50]}...")
            
            print("DEBUG: Antes de chamar send_organized_alert_final")
            try:
                success = self.send_organized_alert_final(parsed_data)
                print("DEBUG: send_organized_alert_final executado com sucesso")
                
                if success:
                    print("SUCCESS: Alerta enviado")
                else:
                    print("ERROR: Falha ao enviar alerta")
            except Exception as e:
                print(f"ERROR: Exce??o ao enviar alerta: {e}")
                import traceback
                traceback.print_exc()
    
    def start_monitoring(self):
        """Inicia monitoramento em tempo real"""
        
        print("INICIANDO SISTEMA DE VIGILANCIA EM TEMPO REAL")
        print("=" * 60)
        print(f"Monitorando: Canal #desarrollo (G459BR2E9)")
        print(f"Respondendo em: Canal #monitor-inventarios (C09HX1HPFPB)")
        print(f"Frequencia: Verificacao a cada 30 segundos")
        print("=" * 60)
        
        self.running = True
        check_count = 0
        
        try:
            while self.running:
                check_count += 1
                print(f"\nVerificacao #{check_count} - {datetime.now().strftime('%H:%M:%S')}")
                
                self.process_new_messages()
                
                print("Aguardando 30 segundos para proxima verificacao...")
                time.sleep(30)
                
        except KeyboardInterrupt:
            print("\nInterrompido pelo usuario")
            self.running = False
        except Exception as e:
            print(f"\nErro durante monitoramento: {e}")
            self.running = False
        finally:
            print("Sistema de vigilancia encerrado")

def main():
    """Fun??o principal"""
    
    print("SISTEMA DE VIGILANCIA REBUSS - TEMPO REAL")
    print("=" * 60)
    
    if not os.getenv('SLACK_BOT_TOKEN'):
        print("ERROR: SLACK_BOT_TOKEN nao configurado")
        print("Configure no arquivo .env ou variavel de ambiente")
        return
    
    monitor = SistemaFinalIntegrado()
    
    try:
        monitor.start_monitoring()
    except Exception as e:
        print(f"Erro fatal: {e}")
    finally:
        print("Encerrando sistema...")

if __name__ == "__main__":
    main()
