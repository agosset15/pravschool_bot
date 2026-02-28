from typing import cast

from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery, Message
from loguru import logger

from src.core.dto import UserDto
from src.transport.telegram.states import Notification

router = Router(name=__name__)


@router.callback_query(F.data.startswith(Notification.CLOSE.state))
async def on_close_notification(callback: CallbackQuery, bot: Bot, user: UserDto) -> None:
    notification: Message = cast(Message, callback.message)
    notification_id = notification.message_id

    logger.info(f"User {user.log}' closed notification '{notification_id}'")

    try:
        await notification.delete()
        await callback.answer()
        logger.debug(f"Notification '{notification_id}' for user '{user.telegram_id}' deleted")
    except Exception as exception:
        logger.error(f"Failed to delete notification '{notification_id}'. Exception: {exception}")

        try:
            logger.debug(f"Attempting to remove keyboard from notification '{notification_id}'")
            await bot.edit_message_reply_markup(
                chat_id=notification.chat.id,
                message_id=notification.message_id,
                reply_markup=None,
            )
            logger.debug(f"Keyboard removed from notification '{notification_id}'")
        except Exception as exception:
            logger.error(
                f"Failed to remove keyboard from notification '{notification_id}'. "
                f"Exception: {exception}"
            )