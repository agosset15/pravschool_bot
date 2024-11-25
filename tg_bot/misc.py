from pathlib import Path

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder

from netschoolapi import NetSchoolAPI

from tg_bot import config

app_dir: Path = Path(__file__).parent.parent

storage = RedisStorage.from_url(config.REDIS_FSM_URI, key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True))
bot = Bot(config.BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))

ns_sessions: dict[int, NetSchoolAPI] = {}
