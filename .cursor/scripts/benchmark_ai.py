#!/usr/bin/env python3
"""
Script de benchmark para frameworks de IA
Versão: 1.0
Data: 2024-12-19
"""

import time
import json
import numpy as np
from pathlib import Path
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AIBenchmark:
    """Benchmark para frameworks de IA"""
    
    def __init__(self):
        self.results = {}
        self.config_file = Path(".cursor/benchmark_results.json")
    
    def benchmark_pytorch(self):
        """Benchmark PyTorch"""
        logger.info("Executando benchmark PyTorch...")
        
        try:
            import torch
            import torch.nn as nn
            
            # Teste de performance básica
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            
            # Operações de tensor
            start_time = time.time()
            x = torch.randn(1000, 1000, device=device)
            y = torch.randn(1000, 1000, device=device)
            z = torch.matmul(x, y)
            torch.cuda.synchronize() if device.type == 'cuda' else None
            tensor_time = time.time() - start_time
            
            # Teste de rede neural
            start_time = time.time()
            model = nn.Sequential(
                nn.Linear(1000, 512),
                nn.ReLU(),
                nn.Linear(512, 256),
                nn.ReLU(),
                nn.Linear(256, 10)
            ).to(device)
            
            input_data = torch.randn(100, 1000, device=device)
            output = model(input_data)
            torch.cuda.synchronize() if device.type == 'cuda' else None
            model_time = time.time() - start_time
            
            self.results['pytorch'] = {
                'tensor_operations': tensor_time,
                'neural_network': model_time,
                'device': str(device),
                'cuda_available': torch.cuda.is_available()
            }
            
            logger.info(f"PyTorch benchmark concluído - Device: {device}")
            
        except ImportError:
            logger.warning("PyTorch não instalado")
        except Exception as e:
            logger.error(f"Erro no benchmark PyTorch: {e}")
    
    def benchmark_tensorflow(self):
        """Benchmark TensorFlow"""
        logger.info("Executando benchmark TensorFlow...")
        
        try:
            import tensorflow as tf
            
            # Configurar GPU se disponível
            gpus = tf.config.experimental.list_physical_devices('GPU')
            if gpus:
                tf.config.experimental.set_memory_growth(gpus[0], True)
            
            # Teste de performance básica
            start_time = time.time()
            x = tf.random.normal([1000, 1000])
            y = tf.random.normal([1000, 1000])
            z = tf.matmul(x, y)
            tf.config.run_functions_eagerly(False)
            tensor_time = time.time() - start_time
            
            # Teste de modelo Keras
            start_time = time.time()
            model = tf.keras.Sequential([
                tf.keras.layers.Dense(512, activation='relu', input_shape=(1000,)),
                tf.keras.layers.Dense(256, activation='relu'),
                tf.keras.layers.Dense(10)
            ])
            
            input_data = tf.random.normal([100, 1000])
            output = model(input_data)
            model_time = time.time() - start_time
            
            self.results['tensorflow'] = {
                'tensor_operations': tensor_time,
                'keras_model': model_time,
                'gpu_available': len(gpus) > 0
            }
            
            logger.info("TensorFlow benchmark concluído")
            
        except ImportError:
            logger.warning("TensorFlow não instalado")
        except Exception as e:
            logger.error(f"Erro no benchmark TensorFlow: {e}")
    
    def benchmark_jax(self):
        """Benchmark JAX"""
        logger.info("Executando benchmark JAX...")
        
        try:
            import jax
            import jax.numpy as jnp
            
            # Teste de performance básica
            start_time = time.time()
            x = jnp.random.normal(jax.random.PRNGKey(0), (1000, 1000))
            y = jnp.random.normal(jax.random.PRNGKey(1), (1000, 1000))
            z = jnp.dot(x, y)
            tensor_time = time.time() - start_time
            
            # Teste com JIT compilation
            @jax.jit
            def simple_model(x):
                return jnp.tanh(jnp.dot(x, jnp.random.normal(jax.random.PRNGKey(2), (1000, 10))))
            
            start_time = time.time()
            input_data = jnp.random.normal(jax.random.PRNGKey(3), (100, 1000))
            output = simple_model(input_data)
            model_time = time.time() - start_time
            
            self.results['jax'] = {
                'tensor_operations': tensor_time,
                'jit_model': model_time,
                'backend': jax.default_backend()
            }
            
            logger.info(f"JAX benchmark concluído - Backend: {jax.default_backend()}")
            
        except ImportError:
            logger.warning("JAX não instalado")
        except Exception as e:
            logger.error(f"Erro no benchmark JAX: {e}")
    
    def benchmark_numpy(self):
        """Benchmark NumPy"""
        logger.info("Executando benchmark NumPy...")
        
        try:
            import numpy as np
            
            # Teste de performance básica
            start_time = time.time()
            x = np.random.randn(1000, 1000)
            y = np.random.randn(1000, 1000)
            z = np.dot(x, y)
            numpy_time = time.time() - start_time
            
            self.results['numpy'] = {
                'matrix_operations': numpy_time,
                'version': np.__version__
            }
            
            logger.info(f"NumPy benchmark concluído - Versão: {np.__version__}")
            
        except ImportError:
            logger.warning("NumPy não instalado")
        except Exception as e:
            logger.error(f"Erro no benchmark NumPy: {e}")
    
    def benchmark_memory_usage(self):
        """Benchmark de uso de memória"""
        logger.info("Executando benchmark de memória...")
        
        try:
            import psutil
            
            # Teste de alocação de memória
            start_memory = psutil.virtual_memory().used
            
            # Alocar arrays grandes
            arrays = []
            for i in range(10):
                arr = np.random.randn(1000, 1000)
                arrays.append(arr)
            
            end_memory = psutil.virtual_memory().used
            memory_used = (end_memory - start_memory) / (1024 * 1024)  # MB
            
            self.results['memory'] = {
                'memory_used_mb': memory_used,
                'total_memory_gb': psutil.virtual_memory().total / (1024**3),
                'available_memory_gb': psutil.virtual_memory().available / (1024**3)
            }
            
            logger.info(f"Benchmark de memória concluído - Uso: {memory_used:.2f} MB")
            
        except Exception as e:
            logger.error(f"Erro no benchmark de memória: {e}")
    
    def run_all_benchmarks(self):
        """Executa todos os benchmarks"""
        logger.info("=== INICIANDO BENCHMARKS DE IA ===")
        
        self.benchmark_pytorch()
        self.benchmark_tensorflow()
        self.benchmark_jax()
        self.benchmark_numpy()
        self.benchmark_memory_usage()
        
        # Salvar resultados
        self.save_results()
        
        logger.info("=== BENCHMARKS CONCLUÍDOS ===")
    
    def save_results(self):
        """Salva resultados do benchmark"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.results, f, indent=2)
            logger.info(f"Resultados salvos em {self.config_file}")
        except Exception as e:
            logger.error(f"Erro ao salvar resultados: {e}")
    
    def print_summary(self):
        """Imprime resumo dos resultados"""
        print("\n" + "="*50)
        print("RESUMO DOS BENCHMARKS DE IA")
        print("="*50)
        
        for framework, metrics in self.results.items():
            print(f"\n{framework.upper()}:")
            for metric, value in metrics.items():
                if isinstance(value, float):
                    print(f"  {metric}: {value:.4f}s")
                else:
                    print(f"  {metric}: {value}")

def main():
    """Função principal"""
    benchmark = AIBenchmark()
    benchmark.run_all_benchmarks()
    benchmark.print_summary()
    
    print("\nSUCCESS: Benchmarks concluidos com sucesso!")
    print("CHART: Verifique os resultados em .cursor/benchmark_results.json")

if __name__ == "__main__":
    main()
