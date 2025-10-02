import logging
import logging.handlers
import os
import json
import threading
from datetime import datetime
from typing import Optional, Dict, Any, Union
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
                 log_level: LogLevel = LogLevel.INFO,
                 max_bytes: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 5):
        
        self.log_file = log_file
        self.slack_webhook_url = slack_webhook_url
        self.slack_channel = slack_channel
        self.log_level = log_level
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self._lock = threading.Lock()
        
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
        
        # Handler para arquivo com rotação
        file_handler = logging.handlers.RotatingFileHandler(
            self.log_file, 
            maxBytes=self.max_bytes,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
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
            # Usar print para evitar loop circular de logging
            print(f"[LogChannel] Erro ao enviar log para Slack: {e}")
    
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
        with self._lock:
            try:
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
                    
            except Exception as e:
                # Fallback para print em caso de erro crítico no logging
                print(f"[LogChannel] Erro crítico no sistema de logging: {e}")
                print(f"[LogChannel] Mensagem original: {message}")
    
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
    
    def get_log_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas sobre os logs
        
        Returns:
            Dicionário com estatísticas dos logs
        """
        stats = {
            "log_file": self.log_file,
            "log_level": self.log_level.value,
            "slack_configured": bool(self.slack_webhook_url),
            "slack_channel": self.slack_channel,
            "max_bytes": self.max_bytes,
            "backup_count": self.backup_count
        }
        
        # Verificar se arquivo de log existe e obter tamanho
        if os.path.exists(self.log_file):
            stats["file_size_bytes"] = os.path.getsize(self.log_file)
            stats["file_exists"] = True
        else:
            stats["file_size_bytes"] = 0
            stats["file_exists"] = False
            
        return stats
    
    def clear_logs(self) -> bool:
        """
        Limpa o arquivo de log atual (mantém backups)
        
        Returns:
            True se bem-sucedido, False caso contrário
        """
        try:
            with self._lock:
                # Fechar handlers para liberar o arquivo
                for handler in self.logger.handlers[:]:
                    handler.close()
                    self.logger.removeHandler(handler)
                
                # Limpar arquivo atual
                if os.path.exists(self.log_file):
                    with open(self.log_file, 'w', encoding='utf-8') as f:
                        f.write("")
                
                # Reconfigurar handlers
                self._setup_logger()
                return True
        except Exception as e:
            print(f"[LogChannel] Erro ao limpar logs: {e}")
            return False


# Instância global do logger
_global_logger: Optional[LogChannel] = None

def setup_logging(log_file: str = "logs/app.log",
                 slack_webhook_url: Optional[str] = None,
                 slack_channel: Optional[str] = None,
                 log_level: LogLevel = LogLevel.INFO,
                 max_bytes: int = 10 * 1024 * 1024,
                 backup_count: int = 5) -> LogChannel:
    """
    Configura o sistema de logging global
    
    Args:
        log_file: Caminho para o arquivo de log
        slack_webhook_url: URL do webhook do Slack
        slack_channel: Canal do Slack para enviar logs
        log_level: Nível mínimo de log
        max_bytes: Tamanho máximo do arquivo de log antes da rotação
        backup_count: Número de arquivos de backup a manter
    
    Returns:
        Instância do LogChannel configurada
    """
    global _global_logger
    _global_logger = LogChannel(
        log_file=log_file, 
        slack_webhook_url=slack_webhook_url, 
        slack_channel=slack_channel, 
        log_level=log_level,
        max_bytes=max_bytes,
        backup_count=backup_count
    )
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

def get_log_stats() -> Dict[str, Any]:
    """Retorna estatísticas do logger global"""
    return get_logger().get_log_stats()

def clear_logs() -> bool:
    """Limpa os logs do logger global"""
    return get_logger().clear_logs()