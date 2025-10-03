#!/usr/bin/env python3
"""
Configurações consolidadas do Sistema Rebuss
Este arquivo centraliza todas as configurações do projeto
"""

import os
from dataclasses import dataclass
from typing import Optional, Dict, Any
from pathlib import Path


@dataclass
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
        """Valida se as configurações necessárias estão presentes"""
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


@dataclass
class SlackConfig:
    """Configurações para integração com o Slack"""
    
    # Token do bot (Bot User OAuth Token)
    SLACK_BOT_TOKEN: Optional[str] = os.getenv('SLACK_BOT_TOKEN')
    
    # ID do canal onde o bot recebe logs
    SLACK_CHANNEL_ID: Optional[str] = os.getenv('SLACK_CHANNEL_ID')
    
    # Nome do canal (para exibição)
    SLACK_CHANNEL_NAME: str = os.getenv('SLACK_CHANNEL_NAME', '#rebuss-logs')
    
    # ID do bot (opcional, para filtrar apenas mensagens do bot)
    BOT_USER_ID: Optional[str] = os.getenv('BOT_USER_ID')
    
    # Configurações de busca
    DEFAULT_HOURS_BACK: int = int(os.getenv('DEFAULT_HOURS_BACK', '24'))
    MAX_MESSAGES_PER_REQUEST: int = int(os.getenv('MAX_MESSAGES_PER_REQUEST', '100'))
    
    # Configurações de exportação
    EXPORT_DIRECTORY: str = os.getenv('EXPORT_DIRECTORY', 'exports')
    
    @classmethod
    def validate(cls) -> bool:
        """Valida se as configurações necessárias estão presentes"""
        missing = []
        
        if not cls.SLACK_BOT_TOKEN:
            missing.append('SLACK_BOT_TOKEN')
        
        if not cls.SLACK_CHANNEL_ID:
            missing.append('SLACK_CHANNEL_ID')
        
        if missing:
            print(f"❌ Configurações faltando: {', '.join(missing)}")
            return False
        
        return True
    
    @classmethod
    def print_config(cls):
        """Imprime a configuração atual (sem dados sensíveis)"""
        print("📋 Configuração do Slack:")
        print(f"   🤖 Bot Token: {'✅ Configurado' if cls.SLACK_BOT_TOKEN else '❌ Não configurado'}")
        print(f"   📢 Canal ID: {'✅ Configurado' if cls.SLACK_CHANNEL_ID else '❌ Não configurado'}")
        print(f"   📺 Nome do Canal: {cls.SLACK_CHANNEL_NAME}")
        print(f"   🆔 Bot User ID: {'✅ Configurado' if cls.BOT_USER_ID else '❌ Não configurado'}")
        print(f"   ⏰ Horas de busca padrão: {cls.DEFAULT_HOURS_BACK}")
        print(f"   📊 Máx. mensagens por requisição: {cls.MAX_MESSAGES_PER_REQUEST}")
        print(f"   📁 Diretório de exportação: {cls.EXPORT_DIRECTORY}")


@dataclass
class CloudflareConfig:
    """Configurações para integração com Cloudflare Worker"""
    
    worker_url: Optional[str] = os.getenv("CLOUDFLARE_WORKER_URL")
    api_token: Optional[str] = os.getenv("CLOUDFLARE_API_TOKEN")
    account_id: Optional[str] = os.getenv("CLOUDFLARE_ACCOUNT_ID")
    namespace_id: Optional[str] = os.getenv("CLOUDFLARE_KV_NAMESPACE_ID")
    timeout_seconds: int = int(os.getenv("CLOUDFLARE_TIMEOUT_SECONDS", "15"))
    
    @classmethod
    def validate(cls) -> bool:
        """Valida se as configurações mínimas foram fornecidas"""
        if not cls.worker_url:
            print("❌ CLOUDFLARE_WORKER_URL não configurada")
            return False
        return True
    
    @classmethod
    def print_config(cls) -> None:
        """Imprime a configuração atual (sem expor segredos)"""
        print("📋 Configuração do Cloudflare Worker:")
        print(f"   🌐 Worker URL: {'✅' if cls.worker_url else '❌'}")
        print(f"   🔐 API Token: {'✅' if cls.api_token else '❌'}")
        print(f"   🆔 Account ID: {'✅' if cls.account_id else '❌'}")
        print(f"   🗂️  KV Namespace: {'✅' if cls.namespace_id else '❌'}")
        print(f"   ⏱️  Timeout (s): {cls.timeout_seconds}")


@dataclass
class WranglerConfig:
    """Configurações do Wrangler (Cloudflare Workers)"""
    
    project_name: str = os.getenv('WRANGLER_PROJECT_NAME', 'chanfana-openapi')
    compatibility_date: str = os.getenv('WRANGLER_COMPATIBILITY_DATE', '2024-09-27')
    environment: str = os.getenv('ENVIRONMENT', 'production')
    
    @classmethod
    def print_config(cls) -> None:
        """Imprime a configuração atual"""
        print("📋 Configuração do Wrangler:")
        print(f"   📦 Nome do projeto: {cls.project_name}")
        print(f"   📅 Data de compatibilidade: {cls.compatibility_date}")
        print(f"   🌍 Ambiente: {cls.environment}")


@dataclass
class GeneralConfig:
    """Configurações gerais do sistema"""
    
    logs_directory: str = os.getenv('LOGS_DIRECTORY', 'logs')
    exports_directory: str = os.getenv('EXPORTS_DIRECTORY', 'exports')
    default_timeout: int = int(os.getenv('DEFAULT_TIMEOUT', '30'))
    max_retries: int = int(os.getenv('MAX_RETRIES', '3'))
    retry_interval: int = int(os.getenv('RETRY_INTERVAL', '5'))
    
    @classmethod
    def print_config(cls) -> None:
        """Imprime a configuração atual"""
        print("📋 Configurações Gerais:")
        print(f"   📁 Diretório de logs: {cls.logs_directory}")
        print(f"   📁 Diretório de exports: {cls.exports_directory}")
        print(f"   ⏱️  Timeout padrão: {cls.default_timeout}s")
        print(f"   🔄 Máx. tentativas: {cls.max_retries}")
        print(f"   ⏳ Intervalo entre tentativas: {cls.retry_interval}s")


class ConfigManager:
    """Gerenciador centralizado de configurações"""
    
    def __init__(self):
        self.log = LogConfig()
        self.slack = SlackConfig()
        self.cloudflare = CloudflareConfig()
        self.wrangler = WranglerConfig()
        self.general = GeneralConfig()
    
    def validate_all(self) -> bool:
        """Valida todas as configurações"""
        print("🔍 Validando configurações...")
        
        valid = True
        valid &= self.log.validate()
        valid &= self.slack.validate()
        valid &= self.cloudflare.validate()
        
        if valid:
            print("✅ Todas as configurações são válidas!")
        else:
            print("❌ Algumas configurações são inválidas!")
        
        return valid
    
    def print_all_configs(self):
        """Imprime todas as configurações"""
        print("=" * 50)
        print("📋 CONFIGURAÇÕES DO SISTEMA REBUSS")
        print("=" * 50)
        
        self.log.print_config()
        print()
        self.slack.print_config()
        print()
        self.cloudflare.print_config()
        print()
        self.wrangler.print_config()
        print()
        self.general.print_config()
        print("=" * 50)
    
    def get_env_template(self) -> str:
        """Retorna um template de arquivo .env com todas as variáveis"""
        template = """# ===========================================
# CONFIGURAÇÕES DO SISTEMA REBUSS
# ===========================================

# ===========================================
# CONFIGURAÇÕES DE LOG
# ===========================================
LOG_FILE=logs/app.log
LOG_LEVEL=INFO
SEND_WARNINGS_TO_SLACK=true
SEND_ERRORS_TO_SLACK=true
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
SLACK_CHANNEL=#logs

# ===========================================
# CONFIGURAÇÕES DO SLACK
# ===========================================
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_CHANNEL_ID=C1234567890
SLACK_CHANNEL_NAME=#rebuss-logs
BOT_USER_ID=U1234567890
DEFAULT_HOURS_BACK=24
MAX_MESSAGES_PER_REQUEST=100
EXPORT_DIRECTORY=exports

# ===========================================
# CONFIGURAÇÕES DO CLOUDFLARE
# ===========================================
CLOUDFLARE_WORKER_URL=https://your-worker.your-subdomain.workers.dev
CLOUDFLARE_API_TOKEN=your-cloudflare-api-token
CLOUDFLARE_ACCOUNT_ID=your-account-id
CLOUDFLARE_KV_NAMESPACE_ID=your-kv-namespace-id
CLOUDFLARE_TIMEOUT_SECONDS=15

# ===========================================
# CONFIGURAÇÕES DO WRANGLER
# ===========================================
WRANGLER_PROJECT_NAME=chanfana-openapi
WRANGLER_COMPATIBILITY_DATE=2024-09-27
ENVIRONMENT=production

# ===========================================
# CONFIGURAÇÕES GERAIS
# ===========================================
LOGS_DIRECTORY=logs
EXPORTS_DIRECTORY=exports
DEFAULT_TIMEOUT=30
MAX_RETRIES=3
RETRY_INTERVAL=5
"""
        return template
    
    def save_env_template(self, filename: str = "config.example.env"):
        """Salva o template de configuração em um arquivo"""
        template = self.get_env_template()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(template)
        print(f"📁 Template de configuração salvo em: {filename}")
    
    def create_directories(self):
        """Cria os diretórios necessários"""
        directories = [
            self.general.logs_directory,
            self.general.exports_directory,
            self.slack.EXPORT_DIRECTORY
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            print(f"📁 Diretório criado/verificado: {directory}")


# Instância global do gerenciador de configurações
config = ConfigManager()


def main():
    """Função principal para testar as configurações"""
    print("🚀 Sistema de Configurações do Rebuss")
    print()
    
    # Criar diretórios necessários
    config.create_directories()
    print()
    
    # Validar configurações
    config.validate_all()
    print()
    
    # Imprimir todas as configurações
    config.print_all_configs()
    
    # Salvar template de configuração
    config.save_env_template()


if __name__ == "__main__":
    main()
