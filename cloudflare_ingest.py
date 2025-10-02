import json
from typing import List

import requests

from cloudflare_config import CloudflareConfig
from slack_log_reader import SlackLogEntry


class CloudflareWorkerClient:
    """Cliente para enviar logs para um Cloudflare Worker."""

    def __init__(self):
        if not CloudflareConfig.validate():
            raise ValueError("Configuração do Cloudflare inválida")

    def send_logs(self, logs: List[SlackLogEntry]) -> bool:
        """Envia logs para o worker."""
        if not logs:
            print("⚠️  Nenhum log para enviar ao Worker")
            return False

        payload = {
            "logs": [log.to_dict() for log in logs],
            "metadata": {
                "source": "slack",
                "count": len(logs),
            },
        }

        headers = {"Content-Type": "application/json"}
        if CloudflareConfig.api_token:
            headers["Authorization"] = f"Bearer {CloudflareConfig.api_token}"

        response = requests.post(
            CloudflareConfig.worker_url,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers=headers,
            timeout=CloudflareConfig.timeout_seconds,
        )

        if response.status_code >= 400:
            print(
                f"❌ Falha ao enviar logs ({response.status_code}): {response.text[:200]}"
            )
            return False

        print(f"✅ {len(logs)} logs enviados para Cloudflare Worker")
        return True
