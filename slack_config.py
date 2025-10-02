#!/usr/bin/env python3
"""
Configurações específicas para integração com o Slack
"""

import os
from typing import Optional

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
        """
        Valida se as configurações necessárias estão presentes
        
        Returns:
            True se as configurações são válidas
        """
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
    
    @classmethod
    def get_setup_instructions(cls):
        """Retorna instruções de configuração"""
        instructions = """
🔧 INSTRUÇÕES DE CONFIGURAÇÃO:

1. TOKEN DO BOT:
   - Vá para: https://api.slack.com/apps
   - Selecione o app 'Rebuss Log Bot'
   - Em 'OAuth & Permissions'
   - Copie o 'Bot User OAuth Token' (começa com xoxb-)
   - Defina: SLACK_BOT_TOKEN=xoxb-...

2. CHANNEL ID:
   - No Slack, vá para o canal onde o bot recebe logs
   - Clique com botão direito no nome do canal
   - Selecione 'View channel details'
   - Copie o Channel ID (formato: C1234567890)
   - Defina: SLACK_CHANNEL_ID=C1234567890

3. BOT USER ID (opcional):
   - No Slack, clique no nome do bot
   - Copie o User ID (formato: U1234567890)
   - Defina: BOT_USER_ID=U1234567890

4. VARIÁVEIS DE AMBIENTE:
   Crie um arquivo .env ou defina as variáveis:
   
   SLACK_BOT_TOKEN=xoxb-your-token-here
   SLACK_CHANNEL_ID=C1234567890
   BOT_USER_ID=U1234567890
   SLACK_CHANNEL_NAME=#rebuss-logs
   DEFAULT_HOURS_BACK=24
   MAX_MESSAGES_PER_REQUEST=100
   EXPORT_DIRECTORY=exports

5. PERMISSÕES NECESSÁRIAS:
   O bot precisa das seguintes permissões:
   - channels:history (ler histórico do canal)
   - chat:read (ler mensagens)
   - users:read (ler informações de usuários)
        """
        return instructions
