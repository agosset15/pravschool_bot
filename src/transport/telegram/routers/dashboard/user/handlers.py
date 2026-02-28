from typing import cast

from aiogram import Bot
from aiogram.types import Document, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput
from dishka.integrations.aiogram_dialog import FromDishka, inject

from src.core.config import AppConfig
from src.infrastructure.taskiq.tasks.schedule import parse_schedule
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
