from dataclasses import dataclass
from typing import Optional

from aiogram_dialog import DialogManager, DialogProtocol
from aiogram_dialog import Window as WindowProtocol
from aiogram_dialog.api.entities import NewMessage


@dataclass
class NewMessageWithEffect(NewMessage):
    message_effect_id: Optional[str] = None


class Window(WindowProtocol):
    async def render(self, dialog: DialogProtocol, manager: DialogManager) -> NewMessage:
        new_message = await super().render(dialog, manager)

        return NewMessageWithEffect(
            chat=new_message.chat,
            thread_id=new_message.thread_id,
            business_connection_id=new_message.business_connection_id,
            text=new_message.text,
            reply_markup=new_message.reply_markup,
            parse_mode=new_message.parse_mode,
            show_mode=new_message.show_mode,
            media=new_message.media,
            link_preview_options=new_message.link_preview_options,
            message_effect_id=getattr(manager, "message_effect_id", None),
        )