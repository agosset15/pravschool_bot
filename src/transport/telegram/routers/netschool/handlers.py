from datetime import date, timedelta
from typing import cast

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button, Select
from dishka.integrations.aiogram_dialog import FromDishka, inject
from fluentogram import TranslatorRunner

from src.transport.telegram.states import NetSchool


@inject
async def on_ns_day_selected(
    callback: CallbackQuery,
    widget: Select,
    dialog_manager: DialogManager,
    day_number: int,
    i18n: FromDishka[TranslatorRunner],
) -> None:
    start_date = date.fromisoformat(dialog_manager.dialog_data["start"])
    dialog_manager.dialog_data["day"] = (start_date + timedelta(days=day_number)).isoformat()

    await callback.answer(text=i18n.get("loading"))
    await dialog_manager.switch_to(NetSchool.DAY)


@inject
async def on_ns_change_student(
    callback: CallbackQuery,
    widget: Select,
    dialog_manager: DialogManager,
    student_id: int,
    i18n: FromDishka[TranslatorRunner],
) -> None:
    dialog_manager.dialog_data["student_id"] = student_id

    await callback.answer(text=i18n.get("loading"))
    await dialog_manager.switch_to(NetSchool.DAY)


@inject
async def on_change_week(
    callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
) -> None:
    dest = cast(str, widget.widget_id)
    start_date = date.fromisoformat(dialog_manager.dialog_data["start"])
    end_date = date.fromisoformat(dialog_manager.dialog_data["end"])

    delta = timedelta(days=7)
    if dest == "prev_week":
        delta = -delta
    start_date += delta
    end_date += delta
    dialog_manager.dialog_data["start"] = start_date.isoformat()
    dialog_manager.dialog_data["end"] = end_date.isoformat()

    await dialog_manager.switch_to(NetSchool.MAIN)
