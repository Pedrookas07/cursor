import logging
import os
import json
from datetime import datetime
from typing import Optional, Dict, Any
import requests
from enum import Enum

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LogChannel:
    """
    Sistema de logs que suporta múltiplos canais de saída:
    - Arquivo de log
    - Canal do Slack
    - Console
    """
    
    def __init__(self, 
                 log_file: str = "logs/app.log",
                 slack_webhook_url: Optional[str] = None,
                 slack_channel: Optional[str] = None,
                 log_level: LogLevel = LogLevel.INFO):
        
        self.log_file = log_file
        self.slack_webhook_url = slack_webhook_url
        self.slack_channel = slack_channel
        self.log_level = log_level
        
        # Criar diretório de logs se não existir
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Configurar logger
        self._setup_logger()
    
    def _setup_logger(self):
        """Configura o sistema de logging"""
        self.logger = logging.getLogger('LogChannel')
        self.logger.setLevel(getattr(logging, self.log_level.value))
        
        # Limpar handlers existentes
        self.logger.handlers.clear()
        
        # Handler para arquivo
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # Handler para console
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
    
    def _send_to_slack(self, message: str, level: LogLevel, extra_data: Optional[Dict] = None):
        """Envia mensagem para o canal do Slack"""
        if not self.slack_webhook_url:
            return
        
        # Cores baseadas no nível do log
        color_map = {
            LogLevel.DEBUG: "#36a64f",      # Verde
            LogLevel.INFO: "#2196F3",       # Azul
            LogLevel.WARNING: "#ff9800",    # Laranja
            LogLevel.ERROR: "#f44336",      # Vermelho
            LogLevel.CRITICAL: "#9c27b0"    # Roxo
        }
        
        # Emojis baseados no nível do log
        emoji_map = {
            LogLevel.DEBUG: "🔍",
            LogLevel.INFO: "ℹ️",
            LogLevel.WARNING: "⚠️",
            LogLevel.ERROR: "❌",
            LogLevel.CRITICAL: "🚨"
        }
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        payload = {
            "channel": self.slack_channel or "#logs",
            "username": "LogBot",
            "icon_emoji": ":robot_face:",
            "attachments": [
                {
                    "color": color_map.get(level, "#36a64f"),
                    "fields": [
                        {
                            "title": f"{emoji_map.get(level, '📝')} {level.value}",
                            "value": message,
                            "short": False
                        },
                        {
                            "title": "Timestamp",
                            "value": timestamp,
                            "short": True
                        }
                    ]
                }
            ]
        }
        
        # Adicionar dados extras se fornecidos
        if extra_data:
            payload["attachments"][0]["fields"].append({
                "title": "Dados Extras",
                "value": f"```{json.dumps(extra_data, indent=2, ensure_ascii=False)}```",
                "short": False
            })
        
        try:
            response = requests.post(self.slack_webhook_url, json=payload, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            # Log do erro sem enviar para o Slack para evitar loop
            self.logger.error(f"Erro ao enviar log para Slack: {e}")
    
    def log(self, message: str, level: LogLevel = LogLevel.INFO, 
            send_to_slack: bool = False, extra_data: Optional[Dict] = None):
        """
        Registra uma mensagem de log
        
        Args:
            message: Mensagem a ser logada
            level: Nível do log
            send_to_slack: Se deve enviar para o Slack
            extra_data: Dados extras para incluir no log
        """
        # Log para arquivo e console
        log_method = getattr(self.logger, level.value.lower())
        
        if extra_data:
            full_message = f"{message} | Dados: {json.dumps(extra_data, ensure_ascii=False)}"
        else:
            full_message = message
        
        log_method(full_message)
        
        # Enviar para Slack se solicitado
        if send_to_slack:
            self._send_to_slack(message, level, extra_data)
    
    def debug(self, message: str, send_to_slack: bool = False, extra_data: Optional[Dict] = None):
        """Log de debug"""
        self.log(message, LogLevel.DEBUG, send_to_slack, extra_data)
    
    def info(self, message: str, send_to_slack: bool = False, extra_data: Optional[Dict] = None):
        """Log de informação"""
        self.log(message, LogLevel.INFO, send_to_slack, extra_data)
    
    def warning(self, message: str, send_to_slack: bool = True, extra_data: Optional[Dict] = None):
        """Log de aviso (por padrão envia para Slack)"""
        self.log(message, LogLevel.WARNING, send_to_slack, extra_data)
    
    def error(self, message: str, send_to_slack: bool = True, extra_data: Optional[Dict] = None):
        """Log de erro (por padrão envia para Slack)"""
        self.log(message, LogLevel.ERROR, send_to_slack, extra_data)
    
    def critical(self, message: str, send_to_slack: bool = True, extra_data: Optional[Dict] = None):
        """Log crítico (por padrão envia para Slack)"""
        self.log(message, LogLevel.CRITICAL, send_to_slack, extra_data)


# Instância global do logger
_global_logger: Optional[LogChannel] = None

def setup_logging(log_file: str = "logs/app.log",
                 slack_webhook_url: Optional[str] = None,
                 slack_channel: Optional[str] = None,
                 log_level: LogLevel = LogLevel.INFO) -> LogChannel:
    """
    Configura o sistema de logging global
    
    Args:
        log_file: Caminho para o arquivo de log
        slack_webhook_url: URL do webhook do Slack
        slack_channel: Canal do Slack para enviar logs
        log_level: Nível mínimo de log
    
    Returns:
        Instância do LogChannel configurada
    """
    global _global_logger
    _global_logger = LogChannel(log_file, slack_webhook_url, slack_channel, log_level)
    return _global_logger

def get_logger() -> LogChannel:
    """
    Retorna a instância global do logger
    
    Returns:
        Instância do LogChannel
    
    Raises:
        RuntimeError: Se o logging não foi configurado
    """
    if _global_logger is None:
        raise RuntimeError("Logging não foi configurado. Chame setup_logging() primeiro.")
    return _global_logger

# Funções de conveniência
def debug(message: str, send_to_slack: bool = False, extra_data: Optional[Dict] = None):
    """Log de debug usando o logger global"""
    get_logger().debug(message, send_to_slack, extra_data)

def info(message: str, send_to_slack: bool = False, extra_data: Optional[Dict] = None):
    """Log de informação usando o logger global"""
    get_logger().info(message, send_to_slack, extra_data)

def warning(message: str, send_to_slack: bool = True, extra_data: Optional[Dict] = None):
    """Log de aviso usando o logger global"""
    get_logger().warning(message, send_to_slack, extra_data)

def error(message: str, send_to_slack: bool = True, extra_data: Optional[Dict] = None):
    """Log de erro usando o logger global"""
    get_logger().error(message, send_to_slack, extra_data)

def critical(message: str, send_to_slack: bool = True, extra_data: Optional[Dict] = None):
    """Log crítico usando o logger global"""
    get_logger().critical(message, send_to_slack, extra_data)