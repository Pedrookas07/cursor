#!/usr/bin/env python3
"""
Script para salvar todas as configurações do sistema Rebuss
"""

import os
import json
from datetime import datetime
from pathlib import Path
from config_consolidado import ConfigManager


def salvar_configuracoes():
    """Salva todas as configurações em arquivos de backup"""
    
    print("Salvando configurações do sistema Rebuss...")
    
    # Criar diretório de backup se não existir
    backup_dir = Path("config_backup")
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. Salvar configurações em JSON
    config_data = {
        "timestamp": timestamp,
        "log": {
            "LOG_FILE": os.getenv('LOG_FILE', 'logs/app.log'),
            "LOG_LEVEL": os.getenv('LOG_LEVEL', 'INFO'),
            "SLACK_WEBHOOK_URL": "***" if os.getenv('SLACK_WEBHOOK_URL') else None,
            "SLACK_CHANNEL": os.getenv('SLACK_CHANNEL', '#logs'),
            "SEND_WARNINGS_TO_SLACK": os.getenv('SEND_WARNINGS_TO_SLACK', 'true'),
            "SEND_ERRORS_TO_SLACK": os.getenv('SEND_ERRORS_TO_SLACK', 'true')
        },
        "slack": {
            "SLACK_BOT_TOKEN": "***" if os.getenv('SLACK_BOT_TOKEN') else None,
            "SLACK_CHANNEL_ID": os.getenv('SLACK_CHANNEL_ID'),
            "SLACK_CHANNEL_NAME": os.getenv('SLACK_CHANNEL_NAME', '#rebuss-logs'),
            "BOT_USER_ID": os.getenv('BOT_USER_ID'),
            "DEFAULT_HOURS_BACK": os.getenv('DEFAULT_HOURS_BACK', '24'),
            "MAX_MESSAGES_PER_REQUEST": os.getenv('MAX_MESSAGES_PER_REQUEST', '100'),
            "EXPORT_DIRECTORY": os.getenv('EXPORT_DIRECTORY', 'exports')
        },
        "cloudflare": {
            "CLOUDFLARE_WORKER_URL": os.getenv('CLOUDFLARE_WORKER_URL'),
            "CLOUDFLARE_API_TOKEN": "***" if os.getenv('CLOUDFLARE_API_TOKEN') else None,
            "CLOUDFLARE_ACCOUNT_ID": os.getenv('CLOUDFLARE_ACCOUNT_ID'),
            "CLOUDFLARE_KV_NAMESPACE_ID": os.getenv('CLOUDFLARE_KV_NAMESPACE_ID'),
            "CLOUDFLARE_TIMEOUT_SECONDS": os.getenv('CLOUDFLARE_TIMEOUT_SECONDS', '15')
        },
        "wrangler": {
            "WRANGLER_PROJECT_NAME": os.getenv('WRANGLER_PROJECT_NAME', 'chanfana-openapi'),
            "WRANGLER_COMPATIBILITY_DATE": os.getenv('WRANGLER_COMPATIBILITY_DATE', '2024-09-27'),
            "ENVIRONMENT": os.getenv('ENVIRONMENT', 'production')
        },
        "general": {
            "LOGS_DIRECTORY": os.getenv('LOGS_DIRECTORY', 'logs'),
            "EXPORTS_DIRECTORY": os.getenv('EXPORTS_DIRECTORY', 'exports'),
            "DEFAULT_TIMEOUT": os.getenv('DEFAULT_TIMEOUT', '30'),
            "MAX_RETRIES": os.getenv('MAX_RETRIES', '3'),
            "RETRY_INTERVAL": os.getenv('RETRY_INTERVAL', '5')
        }
    }
    
    # Salvar JSON
    json_file = backup_dir / f"config_backup_{timestamp}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=2, ensure_ascii=False)
    print(f"Configurações salvas em JSON: {json_file}")
    
    # 2. Salvar template .env
    env_file = backup_dir / f"config_template_{timestamp}.env"
    config_manager = ConfigManager()
    template = config_manager.get_env_template()
    
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(template)
    print(f"Template .env salvo: {env_file}")
    
    # 3. Salvar configurações atuais em formato legível
    readable_file = backup_dir / f"config_atual_{timestamp}.txt"
    with open(readable_file, 'w', encoding='utf-8') as f:
        f.write(f"CONFIGURAÇÕES DO SISTEMA REBUSS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")
        
        # Logs
        f.write("CONFIGURAÇÕES DE LOG:\n")
        f.write(f"  LOG_FILE: {os.getenv('LOG_FILE', 'logs/app.log')}\n")
        f.write(f"  LOG_LEVEL: {os.getenv('LOG_LEVEL', 'INFO')}\n")
        f.write(f"  SLACK_WEBHOOK_URL: {'Configurado' if os.getenv('SLACK_WEBHOOK_URL') else 'Não configurado'}\n")
        f.write(f"  SLACK_CHANNEL: {os.getenv('SLACK_CHANNEL', '#logs')}\n")
        f.write(f"  SEND_WARNINGS_TO_SLACK: {os.getenv('SEND_WARNINGS_TO_SLACK', 'true')}\n")
        f.write(f"  SEND_ERRORS_TO_SLACK: {os.getenv('SEND_ERRORS_TO_SLACK', 'true')}\n\n")
        
        # Slack
        f.write("CONFIGURAÇÕES DO SLACK:\n")
        f.write(f"  SLACK_BOT_TOKEN: {'Configurado' if os.getenv('SLACK_BOT_TOKEN') else 'Não configurado'}\n")
        f.write(f"  SLACK_CHANNEL_ID: {os.getenv('SLACK_CHANNEL_ID', 'Não configurado')}\n")
        f.write(f"  SLACK_CHANNEL_NAME: {os.getenv('SLACK_CHANNEL_NAME', '#rebuss-logs')}\n")
        f.write(f"  BOT_USER_ID: {os.getenv('BOT_USER_ID', 'Não configurado')}\n")
        f.write(f"  DEFAULT_HOURS_BACK: {os.getenv('DEFAULT_HOURS_BACK', '24')}\n")
        f.write(f"  MAX_MESSAGES_PER_REQUEST: {os.getenv('MAX_MESSAGES_PER_REQUEST', '100')}\n")
        f.write(f"  EXPORT_DIRECTORY: {os.getenv('EXPORT_DIRECTORY', 'exports')}\n\n")
        
        # Cloudflare
        f.write("CONFIGURAÇÕES DO CLOUDFLARE:\n")
        f.write(f"  CLOUDFLARE_WORKER_URL: {os.getenv('CLOUDFLARE_WORKER_URL', 'Não configurado')}\n")
        f.write(f"  CLOUDFLARE_API_TOKEN: {'Configurado' if os.getenv('CLOUDFLARE_API_TOKEN') else 'Não configurado'}\n")
        f.write(f"  CLOUDFLARE_ACCOUNT_ID: {os.getenv('CLOUDFLARE_ACCOUNT_ID', 'Não configurado')}\n")
        f.write(f"  CLOUDFLARE_KV_NAMESPACE_ID: {os.getenv('CLOUDFLARE_KV_NAMESPACE_ID', 'Não configurado')}\n")
        f.write(f"  CLOUDFLARE_TIMEOUT_SECONDS: {os.getenv('CLOUDFLARE_TIMEOUT_SECONDS', '15')}\n\n")
        
        # Wrangler
        f.write("CONFIGURAÇÕES DO WRANGLER:\n")
        f.write(f"  WRANGLER_PROJECT_NAME: {os.getenv('WRANGLER_PROJECT_NAME', 'chanfana-openapi')}\n")
        f.write(f"  WRANGLER_COMPATIBILITY_DATE: {os.getenv('WRANGLER_COMPATIBILITY_DATE', '2024-09-27')}\n")
        f.write(f"  ENVIRONMENT: {os.getenv('ENVIRONMENT', 'production')}\n\n")
        
        # Gerais
        f.write("CONFIGURAÇÕES GERAIS:\n")
        f.write(f"  LOGS_DIRECTORY: {os.getenv('LOGS_DIRECTORY', 'logs')}\n")
        f.write(f"  EXPORTS_DIRECTORY: {os.getenv('EXPORTS_DIRECTORY', 'exports')}\n")
        f.write(f"  DEFAULT_TIMEOUT: {os.getenv('DEFAULT_TIMEOUT', '30')}\n")
        f.write(f"  MAX_RETRIES: {os.getenv('MAX_RETRIES', '3')}\n")
        f.write(f"  RETRY_INTERVAL: {os.getenv('RETRY_INTERVAL', '5')}\n")
    
    print(f"Configurações atuais salvas: {readable_file}")
    
    # 4. Salvar wrangler.toml
    wrangler_file = backup_dir / f"wrangler_{timestamp}.toml"
    try:
        with open("wrangler.toml", 'r', encoding='utf-8') as src:
            content = src.read()
        with open(wrangler_file, 'w', encoding='utf-8') as dst:
            dst.write(content)
        print(f"wrangler.toml salvo: {wrangler_file}")
    except FileNotFoundError:
        print("Arquivo wrangler.toml não encontrado")
    
    # 5. Salvar requirements.txt
    requirements_file = backup_dir / f"requirements_{timestamp}.txt"
    try:
        with open("requirements.txt", 'r', encoding='utf-8') as src:
            content = src.read()
        with open(requirements_file, 'w', encoding='utf-8') as dst:
            dst.write(content)
        print(f"requirements.txt salvo: {requirements_file}")
    except FileNotFoundError:
        print("Arquivo requirements.txt não encontrado")
    
    # 6. Salvar package.json
    package_file = backup_dir / f"package_{timestamp}.json"
    try:
        with open("package.json", 'r', encoding='utf-8') as src:
            content = src.read()
        with open(package_file, 'w', encoding='utf-8') as dst:
            dst.write(content)
        print(f"package.json salvo: {package_file}")
    except FileNotFoundError:
        print("Arquivo package.json não encontrado")
    
    print(f"\nTodas as configurações foram salvas em: {backup_dir}")
    print(f"Arquivos criados:")
    print(f"   - {json_file.name}")
    print(f"   - {env_file.name}")
    print(f"   - {readable_file.name}")
    if wrangler_file.exists():
        print(f"   - {wrangler_file.name}")
    if requirements_file.exists():
        print(f"   - {requirements_file.name}")
    if package_file.exists():
        print(f"   - {package_file.name}")


def listar_configuracoes_salvas():
    """Lista todas as configurações salvas"""
    backup_dir = Path("config_backup")
    if not backup_dir.exists():
        print("Nenhuma configuração salva encontrada")
        return
    
    print("Configurações salvas:")
    for file in sorted(backup_dir.iterdir()):
        if file.is_file():
            size = file.stat().st_size
            print(f"   - {file.name} ({size} bytes)")


if __name__ == "__main__":
    print("Salvando configurações do Sistema Rebuss")
    print("=" * 50)
    
    salvar_configuracoes()
    print()
    listar_configuracoes_salvas()
