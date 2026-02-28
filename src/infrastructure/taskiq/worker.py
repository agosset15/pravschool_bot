from dishka import AsyncContainer
from dishka.integrations.aiogram import setup_dishka as setup_aiogram_dishka
from dishka.integrations.taskiq import setup_dishka as setup_taskiq_dishka
from taskiq_redis import RedisStreamBroker

from src.container import create_container
from src.core.config import AppConfig
from src.core.logger import setup_logger
from src.transport.telegram.dispatcher import (
    get_bg_manager_factory,
    get_dispatcher,
    setup_dispatcher,
)

from .broker import broker


def worker() -> RedisStreamBroker:
    setup_logger(AppConfig.get())

    config = AppConfig.get()
    dispatcher = get_dispatcher(config)
    bg_manager_factory = get_bg_manager_factory(dispatcher)

    setup_dispatcher(dispatcher)

    container = create_container(config, bg_manager_factory)
    broker.add_dependency_context({AsyncContainer: container})

    setup_taskiq_dishka(container, broker)
    setup_aiogram_dishka(container, dispatcher, auto_inject=True)

    return broker
