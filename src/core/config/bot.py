from pydantic import SecretStr

from src.core.constants import BOT_WEBHOOK_ENDPOINT

from .base import BaseConfig


class BotConfig(BaseConfig, env_prefix="BOT_"):
    token: SecretStr
    secret_token: SecretStr
    owner_id: int
    support_username: SecretStr
    mini_app_path: str = "/app"

    topic_logs_enabled: bool = False
    topic_logs_chat_id: int = 0
    topic_logs_thread_bot: int = 2
    topic_logs_thread_user: int = 4

    reset_webhook: bool = False
    drop_pending_updates: bool = False
    setup_commands: bool = True

    @staticmethod
    def webhook_url(domain: SecretStr) -> SecretStr:
        url = f"https://{domain.get_secret_value()}{BOT_WEBHOOK_ENDPOINT}"
        return SecretStr(url)

    @staticmethod
    def safe_webhook_url(domain: SecretStr) -> str:
        return f"https://{domain}{BOT_WEBHOOK_ENDPOINT}"

    @property
    def list_topic_logs_threads(self) -> list[int]:
        return [
            self.topic_logs_thread_bot,
            self.topic_logs_thread_user
        ]