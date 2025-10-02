import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class CloudflareConfig:
    """Configurações para integração com Cloudflare Worker"""

    worker_url: Optional[str] = os.getenv("CLOUDFLARE_WORKER_URL")
    api_token: Optional[str] = os.getenv("CLOUDFLARE_API_TOKEN")
    account_id: Optional[str] = os.getenv("CLOUDFLARE_ACCOUNT_ID")
    namespace_id: Optional[str] = os.getenv("CLOUDFLARE_KV_NAMESPACE_ID")
    timeout_seconds: int = int(os.getenv("CLOUDFLARE_TIMEOUT_SECONDS", "15"))

    @classmethod
    def validate(cls) -> bool:
        """Valida se as configurações mínimas foram fornecidas."""
        if not cls.worker_url:
            print("❌ CLOUDFLARE_WORKER_URL não configurada")
            return False
        return True

    @classmethod
    def print_config(cls) -> None:
        """Imprime a configuração atual (sem expor segredos)."""
        print("📋 Configuração do Cloudflare Worker:")
        print(f"   🌐 Worker URL: {'✅' if cls.worker_url else '❌'}")
        print(f"   🔐 API Token: {'✅' if cls.api_token else '❌'}")
        print(f"   🆔 Account ID: {'✅' if cls.account_id else '❌'}")
        print(f"   🗂️  KV Namespace: {'✅' if cls.namespace_id else '❌'}")
        print(f"   ⏱️  Timeout (s): {cls.timeout_seconds}")
