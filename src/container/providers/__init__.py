from dishka import Provider
from dishka.integrations.aiogram import AiogramProvider

from .bot import BotProvider
from .config import ConfigProvider
from .database import DatabaseProvider
from .i18n import I18nProvider
from .retort import RetortProvider
from .services import ServicesProvider


def get_providers() -> list[Provider]:
    return [
        AiogramProvider(),
        BotProvider(),
        ConfigProvider(),
        DatabaseProvider(),
        I18nProvider(),
        RetortProvider(),
        ServicesProvider(),
    ]