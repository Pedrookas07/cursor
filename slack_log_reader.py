#!/usr/bin/env python3
"""
Slack Log Reader - Lê logs do Rebuss Log Bot no Slack

Este script permite ler e processar os logs que o bot Rebuss Log Bot
já está recebendo no Slack.
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import requests
from dataclasses import dataclass

@dataclass
class SlackLogEntry:
    """Representa uma entrada de log do Slack"""
    timestamp: datetime
    channel: str
    user: str
    text: str
    machine_info: Optional[Dict[str, Any]] = None
    log_level: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converte a entrada para dicionário serializável"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "channel": self.channel,
            "user": self.user,
            "text": self.text,
            "log_level": self.log_level,
            "machine_info": self.machine_info,
            "raw_data": self.raw_data,
        }

class SlackLogReader:
    """Classe para ler logs do Slack"""
    
    def __init__(self, 
                 slack_token: str,
                 channel_id: str,
                 bot_user_id: Optional[str] = None):
        """
        Inicializa o leitor de logs do Slack
        
        Args:
            slack_token: Token de acesso do Slack (Bot User OAuth Token)
            channel_id: ID do canal onde o bot está recebendo logs
            bot_user_id: ID do usuário bot (opcional, para filtrar apenas mensagens do bot)
        """
        self.slack_token = slack_token
        self.channel_id = channel_id
        self.bot_user_id = bot_user_id
        self.base_url = "https://slack.com/api"
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {slack_token}',
            'Content-Type': 'application/json'
        })
    
    def get_channel_history(self, 
                           limit: int = 100,
                           oldest: Optional[float] = None,
                           latest: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Obtém histórico de mensagens do canal
        
        Args:
            limit: Número máximo de mensagens (máximo 1000)
            oldest: Timestamp da mensagem mais antiga
            latest: Timestamp da mensagem mais recente
            
        Returns:
            Lista de mensagens do canal
        """
        params = {
            'channel': self.channel_id,
            'limit': min(limit, 1000)
        }
        
        if oldest:
            params['oldest'] = oldest
        if latest:
            params['latest'] = latest
            
        response = self.session.get(f"{self.base_url}/conversations.history", params=params)
        response.raise_for_status()
        
        data = response.json()
        if not data.get('ok'):
            raise Exception(f"Erro na API do Slack: {data.get('error', 'Erro desconhecido')}")
            
        return data.get('messages', [])
    
    def parse_log_message(self, message: Dict[str, Any]) -> Optional[SlackLogEntry]:
        """
        Analisa uma mensagem do Slack e extrai informações de log
        
        Args:
            message: Mensagem do Slack
            
        Returns:
            SlackLogEntry se for uma mensagem de log, None caso contrário
        """
        try:
            # Verificar se é uma mensagem do bot (se bot_user_id foi especificado)
            if self.bot_user_id and message.get('user') != self.bot_user_id:
                return None
            
            text = message.get('text', '')
            timestamp = datetime.fromtimestamp(float(message.get('ts', 0)))
            
            # Tentar extrair informações de log da mensagem
            log_level = self._extract_log_level(text)
            machine_info = self._extract_machine_info(text, message)
            
            return SlackLogEntry(
                timestamp=timestamp,
                channel=self.channel_id,
                user=message.get('user', 'unknown'),
                text=text,
                machine_info=machine_info,
                log_level=log_level,
                raw_data=message
            )
            
        except Exception as e:
            print(f"Erro ao analisar mensagem: {e}")
            return None
    
    def _extract_log_level(self, text: str) -> Optional[str]:
        """Extrai o nível de log do texto da mensagem"""
        text_upper = text.upper()
        
        if any(level in text_upper for level in ['CRITICAL', 'CRÍTICO', '🚨']):
            return 'CRITICAL'
        elif any(level in text_upper for level in ['ERROR', 'ERRO', '❌']):
            return 'ERROR'
        elif any(level in text_upper for level in ['WARNING', 'WARN', 'AVISO', '⚠️']):
            return 'WARNING'
        elif any(level in text_upper for level in ['INFO', 'INFORMAÇÃO', 'ℹ️']):
            return 'INFO'
        elif any(level in text_upper for level in ['DEBUG', '🔍']):
            return 'DEBUG'
        
        return None
    
    def _extract_machine_info(self, text: str, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extrai informações da máquina do texto da mensagem"""
        machine_info = {}
        
        # Tentar extrair informações comuns de inventário
        import re
        
        # IP Address
        ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        ip_match = re.search(ip_pattern, text)
        if ip_match:
            machine_info['ip'] = ip_match.group()
        
        # Hostname
        hostname_pattern = r'\b[A-Za-z0-9\-]+\.local\b|\b[A-Za-z0-9\-]+-PC\b|\b[A-Za-z0-9\-]+-LAPTOP\b'
        hostname_match = re.search(hostname_pattern, text)
        if hostname_match:
            machine_info['hostname'] = hostname_match.group()
        
        # MAC Address
        mac_pattern = r'\b(?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2})\b'
        mac_match = re.search(mac_pattern, text)
        if mac_match:
            machine_info['mac'] = mac_match.group()
        
        # Verificar se há attachments com dados estruturados
        attachments = message.get('attachments', [])
        for attachment in attachments:
            fields = attachment.get('fields', [])
            for field in fields:
                title = field.get('title', '').lower()
                value = field.get('value', '')
                
                if 'machine' in title or 'host' in title or 'sistema' in title:
                    machine_info['system_info'] = value
                elif 'user' in title or 'usuário' in title:
                    machine_info['user'] = value
                elif 'timestamp' in title or 'data' in title:
                    machine_info['log_timestamp'] = value
        
        return machine_info if machine_info else None
    
    def get_recent_logs(self, hours: int = 24, limit: int = 100) -> List[SlackLogEntry]:
        """
        Obtém logs recentes do canal
        
        Args:
            hours: Número de horas para buscar no passado
            limit: Número máximo de mensagens
            
        Returns:
            Lista de SlackLogEntry com os logs encontrados
        """
        # Calcular timestamp de X horas atrás
        oldest_time = time.time() - (hours * 3600)
        
        messages = self.get_channel_history(limit=limit, oldest=oldest_time)
        logs = []
        
        for message in messages:
            log_entry = self.parse_log_message(message)
            if log_entry:
                logs.append(log_entry)
        
        # Ordenar por timestamp (mais recente primeiro)
        logs.sort(key=lambda x: x.timestamp, reverse=True)
        return logs
    
    def get_logs_by_level(self, log_level: str, hours: int = 24) -> List[SlackLogEntry]:
        """
        Obtém logs filtrados por nível
        
        Args:
            log_level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            hours: Número de horas para buscar
            
        Returns:
            Lista de logs do nível especificado
        """
        all_logs = self.get_recent_logs(hours=hours)
        return [log for log in all_logs if log.log_level == log_level.upper()]
    
    def export_logs_to_file(self, logs: List[SlackLogEntry], filename: str):
        """
        Exporta logs para arquivo JSON
        
        Args:
            logs: Lista de logs para exportar
            filename: Nome do arquivo de saída
        """
        export_data = []
        
        for log in logs:
            log_dict = {
                'timestamp': log.timestamp.isoformat(),
                'channel': log.channel,
                'user': log.user,
                'text': log.text,
                'log_level': log.log_level,
                'machine_info': log.machine_info
            }
            export_data.append(log_dict)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ {len(logs)} logs exportados para {filename}")
    
    def print_log_summary(self, logs: List[SlackLogEntry]):
        """Imprime um resumo dos logs"""
        if not logs:
            print("📭 Nenhum log encontrado")
            return
        
        print(f"📊 Resumo de {len(logs)} logs:")
        print(f"   📅 Período: {logs[-1].timestamp.strftime('%d/%m/%Y %H:%M')} - {logs[0].timestamp.strftime('%d/%m/%Y %H:%M')}")
        
        # Contar por nível
        level_counts = {}
        machines = set()
        
        for log in logs:
            level = log.log_level or 'UNKNOWN'
            level_counts[level] = level_counts.get(level, 0) + 1
            
            if log.machine_info and log.machine_info.get('hostname'):
                machines.add(log.machine_info['hostname'])
            elif log.machine_info and log.machine_info.get('ip'):
                machines.add(log.machine_info['ip'])
        
        print("   📈 Por nível:")
        for level, count in sorted(level_counts.items()):
            print(f"      {level}: {count}")
        
        if machines:
            print(f"   🖥️  Máquinas: {len(machines)} ({', '.join(list(machines)[:5])}{'...' if len(machines) > 5 else ''})")

    def send_to_cloudflare_worker(self, logs: List[SlackLogEntry]) -> bool:
        """Envia os logs para um Cloudflare Worker"""
        from cloudflare_config import CloudflareConfig

        if not CloudflareConfig.validate():
            print("❌ Configuração do Cloudflare inválida")
            return False

        payload = {
            "logs": [log.to_dict() for log in logs],
            "metadata": {
                "source": "slack",
                "count": len(logs),
                "generated_at": datetime.utcnow().isoformat(),
            },
        }

        headers = {"Content-Type": "application/json"}
        if CloudflareConfig.api_token:
            headers["Authorization"] = f"Bearer {CloudflareConfig.api_token}"

        response = requests.post(
            CloudflareConfig.worker_url,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            timeout=CloudflareConfig.timeout_seconds,
            headers=headers,
        )
        if response.status_code >= 400:
            print(
                "❌ Falha ao enviar logs para Cloudflare:",
                response.status_code,
                response.text,
            )
            return False

        print(f"✅ {len(logs)} logs enviados para Cloudflare Worker")
        return True


def main():
    """Função principal para demonstração"""
    print("🤖 Slack Log Reader - Rebuss Log Bot")
    print("=" * 50)
    
    # Configurações (devem vir de variáveis de ambiente)
    slack_token = os.getenv('SLACK_BOT_TOKEN')
    channel_id = os.getenv('SLACK_CHANNEL_ID')
    
    if not slack_token or not channel_id:
        print("❌ Configuração necessária:")
        print("   SLACK_BOT_TOKEN: Token do bot do Slack")
        print("   SLACK_CHANNEL_ID: ID do canal onde o bot recebe logs")
        print("\n💡 Para obter o token:")
        print("   1. Vá para https://api.slack.com/apps")
        print("   2. Selecione seu app 'Rebuss Log Bot'")
        print("   3. Em 'OAuth & Permissions', copie o 'Bot User OAuth Token'")
        print("\n💡 Para obter o Channel ID:")
        print("   1. No Slack, clique com botão direito no canal")
        print("   2. Selecione 'View channel details'")
        print("   3. Copie o Channel ID")
        return
    
    try:
        # Criar leitor
        reader = SlackLogReader(slack_token, channel_id)
        
        # Obter logs recentes
        print("📥 Buscando logs das últimas 24 horas...")
        logs = reader.get_recent_logs(hours=24, limit=200)
        
        if not logs:
            print("📭 Nenhum log encontrado nas últimas 24 horas")
            return
        
        # Mostrar resumo
        reader.print_log_summary(logs)
        
        # Exportar logs
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"slack_logs_{timestamp}.json"
        reader.export_logs_to_file(logs, filename)
        
        # Mostrar alguns logs de exemplo
        print(f"\n📋 Últimos 5 logs:")
        for i, log in enumerate(logs[:5], 1):
            print(f"\n{i}. [{log.log_level or 'UNKNOWN'}] {log.timestamp.strftime('%d/%m/%Y %H:%M:%S')}")
            print(f"   📝 {log.text[:100]}{'...' if len(log.text) > 100 else ''}")
            if log.machine_info:
                print(f"   🖥️  {log.machine_info}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")


if __name__ == "__main__":
    main()
