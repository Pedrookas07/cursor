#!/usr/bin/env python3
"""Handler para enviar mensagens ao canal de resposta"""

import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class ResponseChannelHandler:
    """Handler para enviar mensagens ao canal de resposta"""
    
    def __init__(self):
        self.bot_token = os.getenv('SLACK_BOT_TOKEN')
        self.response_channel = os.getenv('SLACK_CHANNEL_ID_RESPONSE')
        self.channel_name = os.getenv('RESPONSE_CHANNEL_NAME', 'monitor-inventarios')
        
    def send_message(self, message, level="INFO", include_timestamp=True):
        """Envia mensagem ao canal de resposta"""
        
        # Emojis por nível
        emojis = {
            "CRITICAL": ":rotating_light:",
            "ERROR": ":x:",
            "WARNING": ":warning:",
            "INFO": ":information_source:",
            "SUCCESS": ":white_check_mark:"
        }
        
        emoji = emojis.get(level, ":information_source:")
        
        # Formatar mensagem
        if include_timestamp:
            timestamp = datetime.now().strftime("%H:%M:%S")
            formatted_message = f"{emoji} **{level}** [{timestamp}]\n{message}"
        else:
            formatted_message = f"{emoji} {message}"
        
        # Payload para Slack API
        payload = {
            "channel": self.response_channel,
            "text": formatted_message,
            "username": "Vigilante Inventarios",
            "icon_emoji": ":robot_face:"
        }
        
        # Enviar mensagem
        url = "https://slack.com/api/chat.postMessage"
        headers = {
            "Authorization": f"Bearer {self.bot_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            if response.json().get("ok"):
                print(f"Mensagem enviada para #{self.channel_name}")
                return True
            else:
                print(f"Erro ao enviar mensagem: {response.json().get('error')}")
                return False
                
        except Exception as e:
            print(f"Erro na requisição: {e}")
            return False
    
    def send_daily_report(self, stats):
        """Envia relatório diário"""
        
        report = f""":bar_chart: **Relatório Diário - Vigilante Inventários**
:calendar: Data: {datetime.now().strftime('%Y-%m-%d')}
:mag: Logs processados: {stats.get('total_logs', 0)}
:x: Errores críticos: {stats.get('critical_errors', 0)}
:warning: Avisos: {stats.get('warnings', 0)}
:white_check_mark: Informações: {stats.get('info', 0)}
:globe_with_meridians: Worker Cloudflare: Online"""
        
        return self.send_message(report, "INFO", False)
    
    def send_critical_alert(self, log_entry):
        """Envia alerta crítico"""
        
        alert = f""":rotating_light: **ALERTA CRÍTICO**
:clock3: {log_entry.get('timestamp', 'N/A')}
:office: {log_entry.get('machine_info', {}).get('inventory_name', 'N/A')}
:x: {log_entry.get('text', 'N/A')}
:bust_in_silhouette: {log_entry.get('user_info', {}).get('user_name', 'N/A')}
:link: {log_entry.get('machine_info', {}).get('url', 'N/A')}"""
        
        return self.send_message(alert, "CRITICAL")
    
    def send_system_status(self, status):
        """Envia status do sistema"""
        
        status_msg = f""":white_check_mark: **Estado del Sistema**
:bar_chart: Status: {status.get('status', 'Unknown')}
:arrows_counterclockwise: Última ejecución: {status.get('last_run', 'N/A')}
:chart_with_upwards_trend: Logs procesados últimas 24h: {status.get('logs_24h', 0)}
:globe_with_meridians: Worker Cloudflare: {status.get('worker_status', 'Unknown')}"""
        
        return self.send_message(status_msg, "SUCCESS", False)

# Exemplo de uso
if __name__ == "__main__":
    handler = ResponseChannelHandler()
    
    # Teste de mensagem
    handler.send_message("Sistema de vigilância iniciado com sucesso!", "SUCCESS")
    
    # Teste de relatório
    stats = {
        "total_logs": 15,
        "critical_errors": 3,
        "warnings": 7,
        "info": 5
    }
    handler.send_daily_report(stats)
