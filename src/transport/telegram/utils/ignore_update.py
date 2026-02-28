from aiogram.types import Message
from aiogram_dialog import DialogManager, DialogProtocol, ShowMode
from aiogram_dialog.widgets.input import BaseInput


class IgnoreUpdate(BaseInput):
    async def process_message(
        self,
        message: Message,
        dialog: DialogProtocol,
        manager: DialogManager,
    ) -> bool:
        manager.show_mode = ShowMode.NO_UPDATE
        return True