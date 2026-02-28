from dishka import Provider, Scope, from_context

from src.core.config import AppConfig


class ConfigProvider(Provider):
    scope = Scope.APP

    config = from_context(provides=AppConfig)