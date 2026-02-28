from typing import cast

from aiogram import Bot
from aiogram.types import Document, Message, PhotoSize
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput
from dishka.integrations.aiogram_dialog import FromDishka, inject

from src.core.config import AppConfig
from src.infrastructure.taskiq.tasks.schedule import parse_schedule
from src.services.schedules_extra import SchedulesExtraService
from src.transport.telegram.states import AdminDashboard


@inject
async def on_add_schedule(
    message: Message,
    widget: MessageInput,
    dialog_manager: DialogManager,
    bot: FromDishka[Bot],
    config: FromDishka[AppConfig],
):
    document = cast(Document, message.document)
    document_path = config.temp_file_path(document.file_id+".xlsx")
    await bot.download(document, destination=document_path)
    await parse_schedule.kiq(document_path, message.text)  # ty:ignore[no-matching-overload]

    await dialog_manager.switch_to(AdminDashboard.MAIN)

@inject
async def on_add_photo(
    message: Message,
    widget: MessageInput,
    dialog_manager: DialogManager,
    schedules_extra_service: FromDishka[SchedulesExtraService],
):
    photo = cast(list[PhotoSize],message.photo)[-1]
    schedules_extra = await schedules_extra_service.get()
    schedules_extra.year_photo_id = photo.file_id
    await schedules_extra_service.update(schedules_extra)

    await dialog_manager.switch_to(AdminDashboard.MAIN)
