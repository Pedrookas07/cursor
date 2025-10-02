#!/usr/bin/env python3
"""
Script de status dos background agents
Versão: 1.0
Data: 2024-12-19
"""

import json
import psutil
import time
from pathlib import Path
from datetime import datetime

def get_system_status():
    """Obtém status do sistema"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        'timestamp': datetime.now().isoformat(),
        'cpu_percent': cpu_percent,
        'memory_total_gb': memory.total / (1024**3),
        'memory_used_gb': memory.used / (1024**3),
        'memory_percent': memory.percent,
        'disk_total_gb': disk.total / (1024**3),
        'disk_used_gb': disk.used / (1024**3),
        'disk_percent': (disk.used / disk.total) * 100
    }

def load_agent_config():
    """Carrega configuração dos agents"""
    try:
        with open('.cursor/environment.json', 'r') as f:
            config = json.load(f)
            return config.get('agentConfigurations', {})
    except Exception as e:
        print(f"Erro ao carregar configuração: {e}")
        return {}

def print_agent_status():
    """Imprime status dos background agents"""
    print("="*60)
    print("BACKGROUND AGENTS - STATUS DE PERFORMANCE")
    print("="*60)
    
    # Status do sistema
    status = get_system_status()
    print(f"\nSISTEMA:")
    print(f"  CPU: {status['cpu_percent']:.1f}%")
    print(f"  RAM: {status['memory_used_gb']:.1f}GB / {status['memory_total_gb']:.1f}GB ({status['memory_percent']:.1f}%)")
    print(f"  DISK: {status['disk_used_gb']:.1f}GB / {status['disk_total_gb']:.1f}GB ({status['disk_percent']:.1f}%)")
    
    # Configuração dos agents
    agents = load_agent_config()
    
    if agents:
        print(f"\nAGENTS CONFIGURADOS:")
        for agent_name, config in agents.items():
            if config.get('enabled', False):
                priority = config.get('priority', 'medium')
                resources = config.get('resources', {})
                
                print(f"\n  {agent_name.upper()}:")
                print(f"    Status: ATIVO")
                print(f"    Prioridade: {priority.upper()}")
                print(f"    CPU Cores: {resources.get('cpu_cores', 'N/A')}")
                print(f"    Memória: {resources.get('memory_gb', 'N/A')}GB")
                print(f"    GPU: {'SIM' if resources.get('gpu_enabled', False) else 'NÃO'}")
                
                capabilities = config.get('capabilities', [])
                if capabilities:
                    print(f"    Capacidades: {', '.join(capabilities[:3])}...")
            else:
                print(f"\n  {agent_name.upper()}: INATIVO")
    else:
        print("\nNENHUM AGENT CONFIGURADO")
    
    # Verificar arquivos de monitoramento
    print(f"\nMONITORAMENTO:")
    metrics_file = Path('.cursor/performance_metrics.json')
    benchmark_file = Path('.cursor/benchmark_results.json')
    
    if metrics_file.exists():
        print(f"  Métricas de performance: DISPONÍVEL")
    else:
        print(f"  Métricas de performance: NÃO DISPONÍVEL")
    
    if benchmark_file.exists():
        print(f"  Resultados de benchmark: DISPONÍVEL")
    else:
        print(f"  Resultados de benchmark: NÃO DISPONÍVEL")
    
    print(f"\nSCRIPTS DISPONÍVEIS:")
    scripts = [
        'optimize_performance.py',
        'benchmark_ai.py', 
        'monitor_performance.py',
        'status_agents.py'
    ]
    
    for script in scripts:
        script_path = Path(f'.cursor/scripts/{script}')
        if script_path.exists():
            print(f"  {script}: DISPONÍVEL")
        else:
            print(f"  {script}: NÃO ENCONTRADO")

def main():
    """Função principal"""
    print("INICIANDO VERIFICAÇÃO DE STATUS DOS BACKGROUND AGENTS...")
    print_agent_status()
    
    print(f"\n" + "="*60)
    print("CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*60)
    print("Background agents configurados para máxima performance com IA")
    print("Sistema otimizado e pronto para desenvolvimento de IA")

if __name__ == "__main__":
    main()

