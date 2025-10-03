#!/usr/bin/env python3
"""
Script para mostrar um resumo das configurações salvas
"""

import os
from pathlib import Path
from datetime import datetime


def mostrar_resumo():
    """Mostra um resumo das configurações salvas"""
    
    print("=" * 60)
    print("RESUMO DAS CONFIGURAÇÕES SALVAS - SISTEMA REBUSS")
    print("=" * 60)
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Verificar arquivos principais
    arquivos_principais = [
        "config_consolidado.py",
        "config.example.env", 
        "salvar_configuracoes.py",
        "CONFIGURACOES_README.md"
    ]
    
    print("ARQUIVOS PRINCIPAIS CRIADOS:")
    for arquivo in arquivos_principais:
        if Path(arquivo).exists():
            size = Path(arquivo).stat().st_size
            print(f"  [OK] {arquivo} ({size} bytes)")
        else:
            print(f"  [ERRO] {arquivo} (não encontrado)")
    
    print()
    
    # Verificar diretório de backup
    backup_dir = Path("config_backup")
    if backup_dir.exists():
        print("BACKUPS CRIADOS:")
        arquivos_backup = list(backup_dir.iterdir())
        for arquivo in sorted(arquivos_backup):
            if arquivo.is_file():
                size = arquivo.stat().st_size
                print(f"  [OK] {arquivo.name} ({size} bytes)")
    else:
        print("BACKUPS: Nenhum diretório de backup encontrado")
    
    print()
    
    # Verificar configurações atuais
    print("CONFIGURAÇÕES ATUAIS:")
    print(f"  Diretório de trabalho: {os.getcwd()}")
    print(f"  Python: {os.sys.version}")
    print(f"  Sistema: {os.name}")
    
    # Verificar variáveis de ambiente importantes
    vars_importantes = [
        "LOG_FILE", "LOG_LEVEL", "SLACK_BOT_TOKEN", 
        "CLOUDFLARE_WORKER_URL", "ENVIRONMENT"
    ]
    
    print("\nVARIÁVEIS DE AMBIENTE:")
    for var in vars_importantes:
        valor = os.getenv(var)
        if valor:
            # Mascarar tokens sensíveis
            if "TOKEN" in var or "URL" in var:
                valor = "***" if valor else "Não configurado"
            print(f"  {var}: {valor}")
        else:
            print(f"  {var}: Não configurado")
    
    print()
    
    # Instruções de uso
    print("COMO USAR:")
    print("1. Para ver configurações: python config_consolidado.py")
    print("2. Para salvar backup: python salvar_configuracoes.py")
    print("3. Para configurar: copie config.example.env para .env")
    print("4. Para documentação: leia CONFIGURACOES_README.md")
    
    print()
    print("=" * 60)
    print("CONFIGURAÇÕES SALVAS COM SUCESSO!")
    print("=" * 60)


if __name__ == "__main__":
    mostrar_resumo()
