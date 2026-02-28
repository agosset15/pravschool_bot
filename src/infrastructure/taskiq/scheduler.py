from taskiq import TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource

from src.core.config import AppConfig
from src.core.logger import setup_logger

from .broker import broker


def scheduler() -> TaskiqScheduler:
    setup_logger(AppConfig.get())

    new_scheduler = TaskiqScheduler(
        broker=broker,
        sources=[LabelScheduleSource(broker)],
    )

    return new_scheduler