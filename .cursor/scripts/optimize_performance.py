#!/usr/bin/env python3
"""
Script de otimização de performance para background agents
Versão: 1.0
Data: 2024-12-19
"""

import os
import sys
import psutil
import subprocess
import json
from pathlib import Path
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PerformanceOptimizer:
    """Otimizador de performance para background agents"""
    
    def __init__(self):
        self.config_file = Path(".cursor/environment.json")
        self.load_config()
    
    def load_config(self):
        """Carrega configuração do environment.json"""
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
            logger.info("Configuração carregada com sucesso")
        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {e}")
            self.config = {}
    
    def optimize_memory(self):
        """Otimiza uso de memória"""
        logger.info("Iniciando otimização de memória...")
        
        # Limpar cache do sistema
        if os.name == 'nt':  # Windows
            subprocess.run(['cleanmgr', '/sagerun:1'], capture_output=True)
        else:  # Linux/Mac
            subprocess.run(['sync'], capture_output=True)
            subprocess.run(['echo', '3'], stdout=open('/proc/sys/vm/drop_caches', 'w'))
        
        # Configurar garbage collection
        import gc
        gc.set_threshold(700, 10, 10)
        gc.collect()
        
        logger.info("Otimização de memória concluída")
    
    def optimize_cpu(self):
        """Otimiza uso de CPU"""
        logger.info("Iniciando otimização de CPU...")
        
        # Configurar prioridade de processo
        current_process = psutil.Process()
        current_process.nice(psutil.HIGH_PRIORITY_CLASS)
        
        # Configurar afinidade de CPU
        cpu_count = psutil.cpu_count()
        if cpu_count > 4:
            # Usar apenas os cores mais rápidos
            current_process.cpu_affinity(list(range(cpu_count - 2, cpu_count)))
        
        logger.info("Otimização de CPU concluída")
    
    def optimize_gpu(self):
        """Otimiza uso de GPU"""
        logger.info("Iniciando otimização de GPU...")
        
        try:
            import torch
            if torch.cuda.is_available():
                # Configurar CUDA para máxima performance
                torch.backends.cudnn.benchmark = True
                torch.backends.cudnn.deterministic = False
                torch.backends.cuda.matmul.allow_tf32 = True
                torch.backends.cudnn.allow_tf32 = True
                
                # Limpar cache da GPU
                torch.cuda.empty_cache()
                
                logger.info(f"GPU otimizada: {torch.cuda.get_device_name()}")
            else:
                logger.warning("CUDA não disponível")
        except ImportError:
            logger.warning("PyTorch não instalado")
        except Exception as e:
            logger.error(f"Erro na otimização de GPU: {e}")
    
    def optimize_network(self):
        """Otimiza configurações de rede"""
        logger.info("Iniciando otimização de rede...")
        
        # Configurar TCP para alta performance
        if os.name == 'nt':  # Windows
            subprocess.run([
                'netsh', 'int', 'tcp', 'set', 'global', 'autotuninglevel=normal'
            ], capture_output=True)
        else:  # Linux
            subprocess.run([
                'sysctl', '-w', 'net.core.rmem_max=16777216'
            ], capture_output=True)
            subprocess.run([
                'sysctl', '-w', 'net.core.wmem_max=16777216'
            ], capture_output=True)
        
        logger.info("Otimização de rede concluída")
    
    def setup_monitoring(self):
        """Configura monitoramento de performance"""
        logger.info("Configurando monitoramento...")
        
        # Criar script de monitoramento
        monitor_script = """
import psutil
import time
import json
from datetime import datetime

def monitor_performance():
    while True:
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_io': psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else None,
            'network_io': psutil.net_io_counters()._asdict() if psutil.net_io_counters() else None
        }
        
        # Salvar métricas
        with open('.cursor/performance_metrics.json', 'a') as f:
            f.write(json.dumps(metrics) + '\\n')
        
        time.sleep(60)  # Monitorar a cada minuto

if __name__ == "__main__":
    monitor_performance()
"""
        
        with open('.cursor/scripts/monitor_performance.py', 'w') as f:
            f.write(monitor_script)
        
        logger.info("Monitoramento configurado")
    
    def optimize_ai_frameworks(self):
        """Otimiza frameworks de IA"""
        logger.info("Otimizando frameworks de IA...")
        
        optimizations = []
        
        # PyTorch optimizations
        try:
            import torch
            if torch.cuda.is_available():
                optimizations.append("PyTorch CUDA otimizado")
        except ImportError:
            pass
        
        # TensorFlow optimizations
        try:
            import tensorflow as tf
            tf.config.optimizer.set_jit(True)
            tf.config.threading.set_intra_op_parallelism_threads(0)
            tf.config.threading.set_inter_op_parallelism_threads(0)
            optimizations.append("TensorFlow otimizado")
        except ImportError:
            pass
        
        # JAX optimizations
        try:
            import jax
            jax.config.update('jax_enable_x64', False)
            optimizations.append("JAX otimizado")
        except ImportError:
            pass
        
        logger.info(f"Frameworks otimizados: {', '.join(optimizations)}")
    
    def run_optimization(self):
        """Executa todas as otimizações"""
        logger.info("=== INICIANDO OTIMIZAÇÃO DE PERFORMANCE ===")
        
        try:
            self.optimize_memory()
            self.optimize_cpu()
            self.optimize_gpu()
            self.optimize_network()
            self.optimize_ai_frameworks()
            self.setup_monitoring()
            
            logger.info("=== OTIMIZAÇÃO CONCLUÍDA COM SUCESSO ===")
            
        except Exception as e:
            logger.error(f"Erro durante otimização: {e}")
            return False
        
        return True

def main():
    """Função principal"""
    optimizer = PerformanceOptimizer()
    success = optimizer.run_optimization()
    
    if success:
        print("SUCCESS: Otimizacao de performance concluida com sucesso!")
        print("ROCKET: Background agents configurados para maxima performance")
    else:
        print("ERROR: Erro durante otimizacao")
        sys.exit(1)

if __name__ == "__main__":
    main()
