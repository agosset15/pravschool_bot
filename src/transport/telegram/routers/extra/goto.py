from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode, StartMode
from loguru import logger

from src.core.constants import GOTO_PREFIX, TARGET_TELEGRAM_ID
from src.core.dto import UserDto
from src.core.enums import UserRole
from src.transport.telegram.states import DashboardUser, state_from_string

router = Router(name=__name__)


@router.callback_query(F.data.startswith(GOTO_PREFIX))
async def on_goto(callback: CallbackQuery, dialog_manager: DialogManager, user: UserDto) -> None:
    logger.info(f"{user.log} Go to '{callback.data}'")
    data = callback.data.removeprefix(GOTO_PREFIX)  # ty:ignore[unresolved-attribute]

    state = state_from_string(data)

    if not state:
        logger.warning(f"{user.log} Trying go to not exist state '{data}'")
        await callback.answer()
        return

    if state == DashboardUser.MAIN:
        parts = data.split(":")
        target_telegram_id = None

        try:
            target_telegram_id = int(parts[2])
        except ValueError:
            logger.warning(f"{user.log} Invalid target_telegram_id in callback: {parts[2]}")

        await dialog_manager.bg(
            user_id=user.telegram_id,
            chat_id=user.telegram_id,
        ).start(
            state=DashboardUser.MAIN,
            data={TARGET_TELEGRAM_ID: target_telegram_id},
            mode=StartMode.RESET_STACK,
            show_mode=ShowMode.DELETE_AND_SEND,
        )
        logger.debug(f"{user.log} Redirected to user '{target_telegram_id}'")
        await callback.answer()
        return

    logger.debug(f"{user.log} Redirected to '{state}'")
    await dialog_manager.bg(
        user_id=user.telegram_id,
        chat_id=user.telegram_id,
    ).start(
        state=state,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.DELETE_AND_SEND,
    )
    await callback.answer()


@router.message(F.text.startswith("/start " + GOTO_PREFIX))
async def on_goto_message(message: Message, dialog_manager: DialogManager, user: UserDto) -> None:
    logger.info(f"{user.log} Go to '{message.text}'")
    data = message.text.removeprefix("/start " + GOTO_PREFIX)  # ty:ignore[unresolved-attribute]

    state = state_from_string(data)

    if not state:
        logger.warning(f"{user.log} Trying go to not exist state '{data}'")
        return

    await dialog_manager.bg(
        user_id=user.telegram_id,
        chat_id=user.telegram_id,
    ).start(
        state=state,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.DELETE_AND_SEND,
    )


@router.message(F.text.startswith("/user " + GOTO_PREFIX))
async def on_goto_user(message: Message, dialog_manager: DialogManager, user: UserDto) -> None:
    if not user.role == UserRole.DEV:
        logger.warning(f"{user.log} Trying go to user dashboard without admin rights")
        return
    logger.info(f"{user.log} Go to '{message.text}'")
    try:
        target_telegram_id = int(message.text.removeprefix("/user "))  # ty:ignore[unresolved-attribute]
    except ValueError:
        logger.warning(f"{user.log} Invalid user_id in message: {message.text}")
        return

    await dialog_manager.bg(
        user_id=user.telegram_id,
        chat_id=user.telegram_id,
    ).start(
        state=DashboardUser.MAIN,
        data={TARGET_TELEGRAM_ID: target_telegram_id},
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.DELETE_AND_SEND,
    )
