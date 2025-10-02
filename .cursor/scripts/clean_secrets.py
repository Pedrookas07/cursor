#!/usr/bin/env python3
"""
Script para limpar secrets dos arquivos antes do commit
Versão: 1.0
Data: 2024-12-19
"""

import re
import os
from pathlib import Path

def clean_secrets_in_file(file_path):
    """Remove secrets de um arquivo específico"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Padrões de secrets para remover
        patterns = [
            # Slack Bot Tokens
            (r'xoxb-[a-zA-Z0-9-]+', 'xoxb-your-bot-token-here'),
            # Slack Webhook URLs
            (r'https://hooks\.slack\.com/services/[a-zA-Z0-9/]+', 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'),
            # Outros tokens similares
            (r'xoxp-[a-zA-Z0-9-]+', 'xoxp-your-token-here'),
            (r'xoxa-[a-zA-Z0-9-]+', 'xoxa-your-token-here'),
        ]
        
        original_content = content
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[CLEANED] {file_path}")
            return True
        else:
            print(f"[OK] {file_path}")
            return False
            
    except Exception as e:
        print(f"[ERROR] {file_path}: {e}")
        return False

def main():
    """Função principal"""
    print("[INFO] Iniciando limpeza de secrets...")
    
    # Arquivos para limpar
    files_to_clean = [
        "docs/cursor_correct_logger_py_issues.md",
        ".cursor/scripts/setup_monitoring.py"
    ]
    
    cleaned_count = 0
    for file_path in files_to_clean:
        if os.path.exists(file_path):
            if clean_secrets_in_file(file_path):
                cleaned_count += 1
        else:
            print(f"[WARNING] Arquivo não encontrado: {file_path}")
    
    print(f"[SUCCESS] Limpeza concluída! {cleaned_count} arquivo(s) modificado(s)")
    print("[INFO] Agora você pode fazer commit e push com segurança!")

if __name__ == "__main__":
    main()
