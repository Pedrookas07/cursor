# 📝 Sistema de Canal de Logs

Um sistema completo de logging que suporta múltiplos canais de saída, incluindo arquivos locais e integração com Slack.

## 🚀 Características

- ✅ **Múltiplos canais**: Arquivo, console e Slack
- ✅ **Níveis de log**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- ✅ **Integração Slack**: Mensagens formatadas com cores e emojis
- ✅ **Dados extras**: Suporte a dados estruturados em JSON
- ✅ **Configuração flexível**: Via variáveis de ambiente
- ✅ **Fácil de usar**: API simples e intuitiva

## 🛠️ Instalação

1. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

2. **Configure as variáveis de ambiente:**
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

3. **Configure o webhook do Slack (opcional):**
   - Vá para https://api.slack.com/messaging/webhooks
   - Crie um novo webhook para seu workspace
   - Copie a URL e adicione no arquivo `.env`

## 📖 Uso Básico

### Configuração Inicial

```python
from logger import setup_logging, LogLevel
from config import LogConfig

# Configurar o sistema de logging
logger = setup_logging(
    log_file=LogConfig.LOG_FILE,
    slack_webhook_url=LogConfig.SLACK_WEBHOOK_URL,
    slack_channel=LogConfig.SLACK_CHANNEL,
    log_level=LogLevel(LogConfig.LOG_LEVEL)
)
```

### Logging Simples

```python
from logger import info, warning, error, critical

# Logs básicos
info("Aplicação iniciada")
warning("Memória alta detectada")
error("Falha na conexão com banco de dados")
critical("Sistema indisponível")
```

### Logging com Dados Extras

```python
from logger import get_logger

logger = get_logger()

# Log com dados estruturados
logger.info("Usuário logado", send_to_slack=True, extra_data={
    "usuario_id": 123,
    "email": "usuario@exemplo.com",
    "ip": "192.168.1.100"
})

# Log de erro com contexto
logger.error("Falha no pagamento", extra_data={
    "erro_codigo": "PAY001",
    "valor": 99.90,
    "metodo": "cartao_credito",
    "tentativa": 3
})
```

## 🎯 Exemplo Completo

Execute o arquivo de exemplo para ver o sistema em ação:

```bash
python example_usage.py
```

## ⚙️ Configuração

### Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `LOG_FILE` | Caminho do arquivo de log | `logs/app.log` |
| `LOG_LEVEL` | Nível mínimo de log | `INFO` |
| `SLACK_WEBHOOK_URL` | URL do webhook do Slack | - |
| `SLACK_CHANNEL` | Canal do Slack | `#logs` |
| `SEND_WARNINGS_TO_SLACK` | Enviar avisos para Slack | `true` |
| `SEND_ERRORS_TO_SLACK` | Enviar erros para Slack | `true` |

### Níveis de Log

- **DEBUG** 🔍: Informações detalhadas para debugging
- **INFO** ℹ️: Informações gerais sobre o funcionamento
- **WARNING** ⚠️: Avisos sobre situações que merecem atenção
- **ERROR** ❌: Erros que não impedem o funcionamento
- **CRITICAL** 🚨: Erros críticos que podem parar o sistema

## 📱 Integração com Slack

O sistema envia logs formatados para o Slack com:

- **Cores diferentes** para cada nível de log
- **Emojis** para identificação visual rápida
- **Timestamps** para rastreamento temporal
- **Dados extras** formatados em JSON
- **Informações do bot** personalizáveis

### Exemplo de Mensagem no Slack

```
🚨 CRITICAL
Falha crítica no sistema de pagamentos

Timestamp: 2024-01-15 14:30:25

Dados Extras:
{
  "erro_codigo": "PAY_CRITICAL_001",
  "sistema": "pagamentos",
  "impacto": "alto",
  "usuarios_afetados": 1500
}
```

## 🔧 API Reference

### Classe LogChannel

```python
class LogChannel:
    def __init__(self, log_file, slack_webhook_url=None, slack_channel=None, log_level=LogLevel.INFO)
    def log(self, message, level=LogLevel.INFO, send_to_slack=False, extra_data=None)
    def debug(self, message, send_to_slack=False, extra_data=None)
    def info(self, message, send_to_slack=False, extra_data=None)
    def warning(self, message, send_to_slack=True, extra_data=None)
    def error(self, message, send_to_slack=True, extra_data=None)
    def critical(self, message, send_to_slack=True, extra_data=None)
```

### Funções Globais

```python
def setup_logging(...) -> LogChannel
def get_logger() -> LogChannel
def debug(message, send_to_slack=False, extra_data=None)
def info(message, send_to_slack=False, extra_data=None)
def warning(message, send_to_slack=True, extra_data=None)
def error(message, send_to_slack=True, extra_data=None)
def critical(message, send_to_slack=True, extra_data=None)
```

## 📁 Estrutura de Arquivos

```
/workspace/
├── logger.py          # Sistema principal de logging
├── config.py          # Configurações
├── example_usage.py   # Exemplo de uso
├── requirements.txt   # Dependências
├── .env.example      # Exemplo de configuração
├── README.md         # Esta documentação
└── logs/             # Diretório de logs (criado automaticamente)
    └── app.log       # Arquivo de log principal
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob licença MIT. Veja o arquivo LICENSE para detalhes.

---

**Criado com ❤️ para facilitar o monitoramento e debugging de aplicações**