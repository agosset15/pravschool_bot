from typing import cast

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from dishka.integrations.aiogram import FromDishka, inject
from fluentogram import TranslatorRunner

from src.core.constants import LESSON_TIMES
from src.core.dto import MessagePayloadDto
from src.services.notification import NotificationService
from src.transport.telegram.keyboards import get_time_keyboard

router = Router(name=__name__)


@router.callback_query(F.data.startswith("get_time"), F.message.text)
@inject
async def get_time(
    callback: CallbackQuery,
    i18n: FromDishka[TranslatorRunner],
    notification_service: FromDishka[NotificationService],
):
    await callback.answer(text=i18n.get("loading"))
    message = cast(Message, callback.message)
    text = message.html_text
    data = cast(str, callback.data)

    is_week = "-week" in data.lower()
    show = "-show" in data.lower()

    lines = text.split("\n")
    if is_week:
        day = True
        for i, text in enumerate(lines[3:]):
            if text == "":
                day = False
                continue
            if not day:
                day = text != ""
                continue
            if show:
                lines[i + 3] = f"{text.strip()} <i>[{LESSON_TIMES[i % len(LESSON_TIMES)]}]</i>"
            else:
                lines[i + 3] = text.removesuffix(f" <i>[{LESSON_TIMES[i % len(LESSON_TIMES)]}]</i>")
    else:
        for i, text in enumerate(lines[2:]):
            if show:
                lines[i + 2] = f"{text.strip()} <i>[{LESSON_TIMES[i]}]</i>"
            else:
                lines[i + 2] = text.removesuffix(f" <i>[{LESSON_TIMES[i]}]</i>")

    await notification_service.edit_user_notification(
        message,
        MessagePayloadDto(
            i18n_key="simple-text",
            i18n_kwargs={"text": "\n".join(lines)},
            reply_markup=get_time_keyboard(display=not show, week=is_week),
            delete_after=None,
        ),
    )
