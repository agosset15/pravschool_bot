from typing import Optional
from urllib.parse import quote

from aiogram import Bot
from aiogram.utils.web_app import WebAppInitData, safe_parse_webapp_init_data
from fastapi import HTTPException

from src.core.config import AppConfig
from src.core.constants import DEEPLINK_PREFIX, GOTO_PREFIX, T_ME


class BotService:
    def __init__(self, bot: Bot, config: AppConfig):
        self.bot = bot
        self.config = config
        self._bot_username: Optional[str] = None

    async def _get_bot_redirect_url(self) -> str:
        if self._bot_username is None:
            self._bot_username = (await self.bot.get_me()).username
        return f"{T_ME}{self._bot_username}"

    async def get_my_name(self) -> str:
        result = await self.bot.get_my_name()
        return result.name

    async def get_goto_url(self, public_code: str) -> str:
        base_url = await self._get_bot_redirect_url()
        return f"{base_url}{DEEPLINK_PREFIX}{GOTO_PREFIX}{public_code}"

    async def get_referral_url(self, public_code: str) -> str:
        base_url = await self._get_bot_redirect_url()
        return f"{base_url}{DEEPLINK_PREFIX}{public_code}"

    async def get_mini_app_url(self, start_data: Optional[str] = None) -> str:
        base_url = await self._get_bot_redirect_url()
        url = f"{base_url}{self.config.bot.mini_app_path}"
        if start_data:
            url += f"?startapp={start_data}"
        return url

    def get_support_url(self, text: Optional[str]) -> str:
        base_url = f"{T_ME}{self.config.bot.support_username}"
        encoded_text = quote(text or "")
        return f"{base_url}?text={encoded_text}"

    def parse_and_validate_webapp_data(self, auth_data: str) -> Optional[int]:
        try:
            web_app_init_data = safe_parse_webapp_init_data(
                token=self.bot.token, init_data=auth_data
            )
        except ValueError:
            raise HTTPException(status_code=401, detail="WebApp data invalid")
        return web_app_init_data.user.id if web_app_init_data.user else None

    def validate_webapp_data(self, auth_data: str) -> WebAppInitData:
        return safe_parse_webapp_init_data(
                token=self.bot.token, init_data=auth_data
            )
