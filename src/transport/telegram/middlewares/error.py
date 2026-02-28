from typing import Any, Awaitable, Callable, Optional, cast

from aiogram.types import ErrorEvent as AiogramErrorEvent
from aiogram.types import TelegramObject
from aiogram.types import User as AiogramUser
from aiogram_dialog.api.exceptions import (
    InvalidStackIdError,
    OutdatedIntent,
    UnknownIntent,
    UnknownState,
)
from dishka import AsyncContainer
from loguru import logger

from src.core.constants import CONTAINER_KEY
from src.core.dto import MessagePayloadDto, TempUserDto
from src.core.enums import MiddlewareEventType
from src.core.exceptions import MenuRenderError
from src.services.notification import NotificationService
from src.transport.telegram.keyboards import get_user_keyboard

from .base import EventTypedMiddleware


class ErrorMiddleware(EventTypedMiddleware):
    __event_types__ = [MiddlewareEventType.ERROR]

    async def middleware_logic(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        event = cast(AiogramErrorEvent, event)
        aiogram_user: Optional[AiogramUser] = self._get_aiogram_user(data)
        container: AsyncContainer = data[CONTAINER_KEY]

        notification_service: NotificationService = await container.get(NotificationService)

        user = None
        reply_markup = None

        if aiogram_user:
            user = TempUserDto.from_aiogram(aiogram_user)
            reply_markup = get_user_keyboard(user.telegram_id)
            if not isinstance(event.exception, MenuRenderError):
                await notification_service.notify_user(
                    TempUserDto.from_aiogram(aiogram_user),
                    MessagePayloadDto(i18n_key="ntf-error.lost-context-restart")
                )

        if isinstance(
            event.exception,
            (
                InvalidStackIdError,
                OutdatedIntent,
                UnknownIntent,
                UnknownState,
            ),
        ):
            return await handler(event, data)

        await notification_service.error_notify(
            error_id=user.telegram_id if user else event.update.update_id,
            exception=event.exception,
            payload=MessagePayloadDto(
                i18n_key="event-error.general",
                i18n_kwargs={
                    "telegram_id": user.telegram_id if user else False,
                    "name": user.name if user else False,
                    "username": aiogram_user.username if aiogram_user and aiogram_user.username else False,  # noqa: E501
                },
                reply_markup=reply_markup,
            ),
        )
        logger.exception(event.exception)
        return None