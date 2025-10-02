
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
        
        # Salvar m�tricas
        with open('.cursor/performance_metrics.json', 'a') as f:
            f.write(json.dumps(metrics) + '\n')
        
        time.sleep(60)  # Monitorar a cada minuto

if __name__ == "__main__":
    monitor_performance()

