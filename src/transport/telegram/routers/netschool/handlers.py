from datetime import date, timedelta
from typing import cast

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button, Select
from dishka.integrations.aiogram_dialog import FromDishka, inject
from fluentogram import TranslatorRunner

from src.core.constants import USER_KEY
from src.core.dto import UserDto
from src.services.netschool import NetSchoolService
from src.transport.telegram.states import NetSchool


@inject
async def on_ns_day_selected(
    callback: CallbackQuery,
    widget: Select,
    dialog_manager: DialogManager,
    day_number: int,
) -> None:
    start_date: date = dialog_manager.dialog_data["start"]
    dialog_manager.dialog_data["day"] = start_date + timedelta(days=day_number)

    await dialog_manager.switch_to(NetSchool.DAY)


@inject
async def on_ns_change_student(
    callback: CallbackQuery,
    widget: Select,
    dialog_manager: DialogManager,
    student_id: int,
    netschool_service: FromDishka[NetSchoolService],
    i18n: FromDishka[TranslatorRunner],
) -> None:
    user: UserDto = dialog_manager.middleware_data[USER_KEY]
    message = cast(Message, callback.message)
    day: date = dialog_manager.dialog_data["day"]
    day_text = await netschool_service.get_day(user, student_id, day)
    dialog_manager.dialog_data["student_id"] = student_id
    dialog_manager.dialog_data["day_text"] = day_text

    await message.edit_text(i18n.get(
        "msg-netschool-day",
        student_id=student_id,
        day_text=day_text,
        children=dialog_manager.dialog_data["children"]
    ))


@inject
async def on_change_week(
    callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
    i18n: FromDishka[TranslatorRunner],
) -> None:
    dest = cast(str, widget.widget_id)
    message = cast(Message, callback.message)
    start_date: date = dialog_manager.dialog_data["start"]
    end_date: date = dialog_manager.dialog_data["end"]

    delta = timedelta(days=7)
    if dest == "prev_week":
        delta = -delta
    start_date += delta
    end_date += delta
    dialog_manager.dialog_data["start"] = start_date
    dialog_manager.dialog_data["end"] = end_date

    await message.edit_text(i18n.get(
        "msg-netschool-menu",
        week=start_date.strftime("%d.%m.%Y") + " - " + end_date.strftime("%d.%m.%Y")
    ))
