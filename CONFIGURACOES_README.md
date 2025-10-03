# Configurações do Sistema Rebuss

Este documento descreve como as configurações do sistema foram salvas e como utilizá-las.

## Arquivos Criados

### 1. Configurações Consolidadas
- **`config_consolidado.py`** - Arquivo principal com todas as configurações centralizadas
- **`config.example.env`** - Template com todas as variáveis de ambiente necessárias

### 2. Scripts de Backup
- **`salvar_configuracoes.py`** - Script para salvar todas as configurações em backup
- **`config_backup/`** - Diretório com backups das configurações

## Como Usar

### 1. Configurações Atuais
Para ver as configurações atuais do sistema:
```bash
python config_consolidado.py
```

### 2. Salvar Configurações
Para salvar todas as configurações em backup:
```bash
python salvar_configuracoes.py
```

### 3. Configurar Variáveis de Ambiente
1. Copie o arquivo `config.example.env` para `.env`
2. Configure as variáveis necessárias no arquivo `.env`
3. Execute o sistema normalmente

## Estrutura das Configurações

### Logs
- **LOG_FILE**: Arquivo de log (padrão: `logs/app.log`)
- **LOG_LEVEL**: Nível de log (padrão: `INFO`)
- **SLACK_WEBHOOK_URL**: URL do webhook do Slack
- **SLACK_CHANNEL**: Canal do Slack para logs
- **SEND_WARNINGS_TO_SLACK**: Enviar avisos para Slack
- **SEND_ERRORS_TO_SLACK**: Enviar erros para Slack

### Slack
- **SLACK_BOT_TOKEN**: Token do bot do Slack
- **SLACK_CHANNEL_ID**: ID do canal do Slack
- **SLACK_CHANNEL_NAME**: Nome do canal
- **BOT_USER_ID**: ID do bot
- **DEFAULT_HOURS_BACK**: Horas para busca padrão
- **MAX_MESSAGES_PER_REQUEST**: Máximo de mensagens por requisição
- **EXPORT_DIRECTORY**: Diretório de exportação

### Cloudflare
- **CLOUDFLARE_WORKER_URL**: URL do Worker
- **CLOUDFLARE_API_TOKEN**: Token da API
- **CLOUDFLARE_ACCOUNT_ID**: ID da conta
- **CLOUDFLARE_KV_NAMESPACE_ID**: ID do namespace KV
- **CLOUDFLARE_TIMEOUT_SECONDS**: Timeout em segundos

### Wrangler
- **WRANGLER_PROJECT_NAME**: Nome do projeto
- **WRANGLER_COMPATIBILITY_DATE**: Data de compatibilidade
- **ENVIRONMENT**: Ambiente (production/development)

### Gerais
- **LOGS_DIRECTORY**: Diretório de logs
- **EXPORTS_DIRECTORY**: Diretório de exports
- **DEFAULT_TIMEOUT**: Timeout padrão
- **MAX_RETRIES**: Máximo de tentativas
- **RETRY_INTERVAL**: Intervalo entre tentativas

## Validação

O sistema inclui validação automática das configurações:
- Verifica se as URLs são válidas
- Valida tokens e IDs
- Confirma se diretórios existem
- Verifica permissões necessárias

## Backup e Restauração

### Backup Automático
O script `salvar_configuracoes.py` cria backups com timestamp incluindo:
- Configurações em JSON
- Template .env
- Configurações em formato legível
- Arquivos de configuração (wrangler.toml, requirements.txt, package.json)

### Restauração
Para restaurar configurações:
1. Use os arquivos do diretório `config_backup/`
2. Copie o template `.env` desejado
3. Configure as variáveis necessárias
4. Execute o sistema

## Segurança

- Tokens e senhas são mascarados nos logs
- Arquivos de backup não contêm dados sensíveis
- Use variáveis de ambiente para dados confidenciais
- Nunca commite arquivos `.env` com dados reais

## Troubleshooting

### Problemas Comuns
1. **Encoding errors**: Remova emojis dos scripts
2. **Configurações inválidas**: Execute validação com `config_consolidado.py`
3. **Diretórios não existem**: Execute `config.create_directories()`

### Logs
- Verifique o arquivo de log configurado em `LOG_FILE`
- Use `LOG_LEVEL=DEBUG` para mais detalhes
- Configure Slack para receber logs importantes

## Manutenção

### Atualizações
- Atualize o template `.env` quando adicionar novas configurações
- Mantenha backups regulares das configurações
- Documente mudanças importantes

### Limpeza
- Remova backups antigos periodicamente
- Limpe logs antigos conforme necessário
- Mantenha apenas configurações ativas

---

**Data de Criação**: 2025-01-03  
**Versão**: 1.0  
**Autor**: Sistema Rebuss
