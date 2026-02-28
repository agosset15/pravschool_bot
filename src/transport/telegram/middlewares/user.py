from typing import Any, Awaitable, Callable, Optional

from aiogram.types import InlineQuery, Message, TelegramObject
from aiogram.types import User as AiogramUser
from dishka import AsyncContainer
from loguru import logger

from src.core.constants import CONTAINER_KEY, GRADES_KEY, USER_KEY
from src.core.dto import MessagePayloadDto, UserDto
from src.core.enums import MiddlewareEventType, SystemNotificationType, ScheduleType
from src.core.utils.converters import parse_referral_code
from src.services.notification import NotificationService
from src.services.schedule import ScheduleService
from src.services.user import UserService
from src.transport.telegram.keyboards import get_user_keyboard

from .base import EventTypedMiddleware


class UserMiddleware(EventTypedMiddleware):
    __event_types__ = [
        MiddlewareEventType.MESSAGE,
        MiddlewareEventType.CALLBACK_QUERY,
        MiddlewareEventType.ERROR,
        MiddlewareEventType.AIOGD_UPDATE,
        MiddlewareEventType.MY_CHAT_MEMBER,
        MiddlewareEventType.INLINE_QUERY,
    ]

    async def middleware_logic(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        aiogram_user: Optional[AiogramUser] = self._get_aiogram_user(data)

        if aiogram_user is None or aiogram_user.is_bot:
            logger.warning("Terminating middleware: event from bot or missing user")
            return None

        container: AsyncContainer = data[CONTAINER_KEY]
        user_service: UserService = await container.get(UserService)
        notification_service: NotificationService = await container.get(NotificationService)

        user: Optional[UserDto] = await user_service.get(aiogram_user.id)

        if user is None:
            code = None
            if isinstance(event, Message) and event.text:
                code = parse_referral_code(event.text)
            user = await user_service.create(aiogram_user, code)
            await notification_service.system_notify(MessagePayloadDto(
                i18n_key="event-user.registered",
                i18n_kwargs={
                    "telegram_id": user.telegram_id,
                    "username": user.username or False,
                    "name": user.name
                },
                reply_markup=get_user_keyboard(user.telegram_id),
            ), SystemNotificationType.USER_REGISTERED)

        data[USER_KEY] = user

        if isinstance(event, InlineQuery):
            schedule_service: ScheduleService = await container.get(ScheduleService)
            grades = await schedule_service.get_grades(ScheduleType.COMMON, inline_extra=True)
            data[GRADES_KEY] = grades

        return await handler(event, data)
