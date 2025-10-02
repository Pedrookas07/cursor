#!/usr/bin/env python3
"""Pipeline para enviar logs do Slack ao Cloudflare Worker."""

import sys
from datetime import datetime

from cloudflare_config import CloudflareConfig
from cloudflare_ingest import CloudflareWorkerClient
from slack_config import SlackConfig
from slack_log_reader import SlackLogReader


def run(hours: int = None, limit: int = None) -> None:
    """Executa a ingestão de logs do Slack para o Cloudflare Worker."""
    print("🔄 Pipeline Slack -> Cloudflare")

    if not SlackConfig.validate():
        print("❌ Configuração do Slack faltando")
        return

    if not CloudflareConfig.validate():
        print("❌ Configuração do Cloudflare faltando")
        return

    SlackConfig.print_config()
    CloudflareConfig.print_config()

    reader = SlackLogReader(
        slack_token=SlackConfig.SLACK_BOT_TOKEN,
        channel_id=SlackConfig.SLACK_CHANNEL_ID,
        bot_user_id=SlackConfig.BOT_USER_ID,
    )

    hours = hours or SlackConfig.DEFAULT_HOURS_BACK
    limit = limit or SlackConfig.MAX_MESSAGES_PER_REQUEST

    print(
        f"📥 Buscando logs das últimas {hours} horas (limite {limit})"
    )
    logs = reader.get_recent_logs(hours=hours, limit=limit)

    if not logs:
        print("📭 Nenhum log encontrado para enviar")
        return

    print(f"✅ {len(logs)} logs coletados do Slack")

    client = CloudflareWorkerClient()
    if client.send_logs(logs):
        print("🚀 Pipeline concluída com sucesso")
    else:
        print("⚠️  Pipeline concluída com falhas")


if __name__ == "__main__":
    try:
        hours_arg = int(sys.argv[1]) if len(sys.argv) > 1 else None
        limit_arg = int(sys.argv[2]) if len(sys.argv) > 2 else None
    except ValueError:
        print("Uso: python slack_to_cloudflare.py [hours] [limit]")
        sys.exit(1)

    run(hours_arg, limit_arg)
