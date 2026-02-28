from typing import Any, Optional

from dishka import AsyncContainer
from loguru import logger
from taskiq import TaskiqMessage, TaskiqResult
from taskiq.abc.middleware import TaskiqMiddleware

from src.core.dto import MessagePayloadDto
from src.services.notification import NotificationService


class ErrorMiddleware(TaskiqMiddleware):
    async def on_error(
        self,
        message: TaskiqMessage,
        result: TaskiqResult[Any],
        exception: BaseException,
    ) -> None:
        logger.error(f"Task '{message.task_name}' error: {exception}")

        container: Optional[AsyncContainer] = self.broker.custom_dependency_context.get(
            AsyncContainer
        )

        if not container:
            logger.error("Dishka container not found in taskiq broker context")
            return

        try:
            notification_service = await container.get(NotificationService)
            await notification_service.error_notify(
                exception,
                MessagePayloadDto(
                    i18n_key="event-error.general",
                    i18n_kwargs={
                        "telegram_id": False
                    }
                )
            )
        except Exception as e:
            logger.error(f"Failed to publish error event: {e}")
