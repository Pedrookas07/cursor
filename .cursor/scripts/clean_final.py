#!/usr/bin/env python3
"""
Script para limpeza final do sistema
Versão: 1.0 - 2025-01-07
"""

import re
import os

def clean_all_files():
    """Limpa todos os arquivos de caracteres problemáticos"""
    print("Limpando arquivos de caracteres problemáticos...")
    
    files_to_clean = [
        'sistema_final_integrado.py',
        'contextualizador_rebuss.py',
        'parser_rebuss_simples.py'
    ]
    
    for filename in files_to_clean:
        if os.path.exists(filename):
            print(f"Limpando {filename}...")
            
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remover caracteres problemáticos
            content = re.sub(r'[✓✔]', 'OK', content)
            content = re.sub(r'[✗✘]', 'ERRO', content)
            content = re.sub(r'[⚠]', 'AVISO', content)
            content = re.sub(r'[🔍]', '[DEBUG]', content)
            content = re.sub(r'[ℹ]', '[INFO]', content)
            content = re.sub(r'[🚨]', '[CRITICO]', content)
            content = re.sub(r'[→]', '->', content)
            content = re.sub(r'[←]', '<-', content)
            content = re.sub(r'[↑]', '^', content)
            content = re.sub(r'[↓]', 'v', content)
            
            # Remover outros caracteres Unicode problemáticos
            content = re.sub(r'[^\x00-\x7F]', '?', content)
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"  {filename} limpo com sucesso")
        else:
            print(f"  {filename} não encontrado")
    
    print("Limpeza concluída!")

if __name__ == "__main__":
    clean_all_files()

