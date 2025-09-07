#!/usr/bin/env python3
"""
Exemplo de uso do sistema de logging

Este arquivo demonstra como usar o canal de logs criado.
"""

from logger import setup_logging, LogLevel, get_logger
from config import LogConfig
import time

def main():
    """Exemplo principal de uso do sistema de logging"""
    
    print("🚀 Iniciando exemplo do sistema de logging...")
    
    # Validar configuração
    if not LogConfig.validate():
        print("❌ Configuração inválida!")
        return
    
    # Imprimir configuração atual
    LogConfig.print_config()
    
    # Configurar o sistema de logging
    logger = setup_logging(
        log_file=LogConfig.LOG_FILE,
        slack_webhook_url=LogConfig.SLACK_WEBHOOK_URL,
        slack_channel=LogConfig.SLACK_CHANNEL,
        log_level=LogLevel(LogConfig.LOG_LEVEL)
    )
    
    print("\n📝 Testando diferentes níveis de log...\n")
    
    # Teste de logs com diferentes níveis
    logger.debug("Este é um log de debug - apenas no arquivo e console")
    time.sleep(1)
    
    logger.info("Aplicação iniciada com sucesso", send_to_slack=True, extra_data={
        "versao": "1.0.0",
        "ambiente": "desenvolvimento",
        "timestamp_inicio": time.time()
    })
    time.sleep(1)
    
    logger.warning("Este é um aviso - será enviado para o Slack por padrão", extra_data={
        "memoria_uso": "85%",
        "cpu_uso": "45%"
    })
    time.sleep(1)
    
    logger.error("Erro simulado para teste", extra_data={
        "erro_codigo": "E001",
        "modulo": "example_usage",
        "detalhes": "Este é apenas um teste de erro"
    })
    time.sleep(1)
    
    # Exemplo de uso com try/catch
    try:
        # Simular um erro
        resultado = 10 / 0
    except ZeroDivisionError as e:
        logger.error(f"Erro de divisão por zero: {str(e)}", extra_data={
            "operacao": "10 / 0",
            "tipo_erro": type(e).__name__,
            "funcao": "main"
        })
    
    # Exemplo de log crítico
    logger.critical("Sistema crítico - teste de alerta máximo", extra_data={
        "sistema": "core",
        "impacto": "alto",
        "acao_requerida": "verificacao_imediata"
    })
    
    print("\n✅ Teste concluído! Verifique:")
    print(f"   📁 Arquivo de log: {LogConfig.LOG_FILE}")
    print(f"   📢 Canal Slack: {LogConfig.SLACK_CHANNEL}")
    print("\n💡 Dica: Configure a variável SLACK_WEBHOOK_URL para ativar o envio para Slack")

def test_high_volume_logging():
    """Teste de volume alto de logs"""
    print("\n🔄 Testando volume alto de logs...")
    
    logger = get_logger()
    
    for i in range(10):
        logger.info(f"Log de teste #{i+1}", extra_data={
            "iteracao": i+1,
            "timestamp": time.time(),
            "teste": "volume_alto"
        })
        time.sleep(0.5)
    
    print("✅ Teste de volume alto concluído!")

if __name__ == "__main__":
    main()
    
    # Perguntar se quer testar volume alto
    resposta = input("\n❓ Deseja testar logging de volume alto? (s/n): ").lower().strip()
    if resposta in ['s', 'sim', 'y', 'yes']:
        test_high_volume_logging()
    
    print("\n👋 Exemplo finalizado!")