#!/usr/bin/env python3
"""
Script para corrigir problemas de encoding
Versão: 1.0 - 2025-01-07
"""

import re

def clean_text_for_slack(text):
    """Remove caracteres que causam problemas de encoding no Windows"""
    # Remover caracteres especiais que causam problemas
    text = re.sub(r'[✓✔]', 'OK', text)
    text = re.sub(r'[✗✘]', 'ERRO', text)
    text = re.sub(r'[⚠]', 'AVISO', text)
    text = re.sub(r'[🔍]', '[DEBUG]', text)
    text = re.sub(r'[ℹ]', '[INFO]', text)
    text = re.sub(r'[🚨]', '[CRITICO]', text)
    
    # Remover outros caracteres Unicode problemáticos
    text = re.sub(r'[^\x00-\x7F]', '?', text)
    
    return text

def fix_sistema_final_integrado():
    """Corrige o arquivo sistema_final_integrado.py"""
    print("Corrigindo problemas de encoding...")
    
    # Ler o arquivo
    with open('sistema_final_integrado.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Aplicar limpeza
    cleaned_content = clean_text_for_slack(content)
    
    # Salvar o arquivo
    with open('sistema_final_integrado.py', 'w', encoding='utf-8') as f:
        f.write(cleaned_content)
    
    print("Arquivo corrigido com sucesso!")

if __name__ == "__main__":
    fix_sistema_final_integrado()

