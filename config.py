import os
from typing import Optional

class LogConfig:
    """Configurações para o sistema de logging"""
    
    # Configurações de arquivo
    LOG_FILE: str = os.getenv('LOG_FILE', 'logs/app.log')
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    
    # Configurações do Slack
    SLACK_WEBHOOK_URL: Optional[str] = os.getenv('SLACK_WEBHOOK_URL')
    SLACK_CHANNEL: str = os.getenv('SLACK_CHANNEL', '#logs')
    
    # Configurações gerais
    SEND_WARNINGS_TO_SLACK: bool = os.getenv('SEND_WARNINGS_TO_SLACK', 'true').lower() == 'true'
    SEND_ERRORS_TO_SLACK: bool = os.getenv('SEND_ERRORS_TO_SLACK', 'true').lower() == 'true'
    
    @classmethod
    def validate(cls) -> bool:
        """
        Valida se as configurações necessárias estão presentes
        
        Returns:
            True se as configurações são válidas
        """
        if cls.SLACK_WEBHOOK_URL and not cls.SLACK_WEBHOOK_URL.startswith('https://hooks.slack.com/'):
            print(f"⚠️  SLACK_WEBHOOK_URL parece inválida: {cls.SLACK_WEBHOOK_URL}")
            return False
        
        return True
    
    @classmethod
    def print_config(cls):
        """Imprime a configuração atual (sem dados sensíveis)"""
        print("📋 Configuração do Sistema de Logs:")
        print(f"   📁 Arquivo de log: {cls.LOG_FILE}")
        print(f"   📊 Nível de log: {cls.LOG_LEVEL}")
        print(f"   📢 Canal Slack: {cls.SLACK_CHANNEL}")
        print(f"   🔗 Webhook Slack: {'✅ Configurado' if cls.SLACK_WEBHOOK_URL else '❌ Não configurado'}")
        print(f"   ⚠️  Avisos para Slack: {'✅' if cls.SEND_WARNINGS_TO_SLACK else '❌'}")
        print(f"   ❌ Erros para Slack: {'✅' if cls.SEND_ERRORS_TO_SLACK else '❌'}")