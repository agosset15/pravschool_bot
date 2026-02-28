from abc import ABC

from adaptix import Retort
from adaptix.conversion import ConversionRetort
from aiogram import Bot
from redis.asyncio import Redis

from src.core.config import AppConfig


class BaseService(ABC):
    config: AppConfig
    bot: Bot
    redis: Redis

    def __init__(
        self,
        config: AppConfig,
        bot: Bot,
        redis: Redis,
        retort: Retort,
        conversion_retort: ConversionRetort,
    ) -> None:
        self.config = config
        self.bot = bot
        self.redis = redis
        self.retort = retort
        self.conversion_retort = conversion_retort