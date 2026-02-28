from aiogram import Bot
from aiogram.types import Message
from aiogram_dialog.api.entities import NewMessage
from aiogram_dialog.manager.message_manager import SEND_METHODS
from aiogram_dialog.manager.message_manager import MessageManager as MessageManagerProtocol


class MessageManager(MessageManagerProtocol):
    async def send_text(self, bot: Bot, new_message: NewMessage) -> Message:
        return await bot.send_message(
            new_message.chat.id,
            text=new_message.text,  # type: ignore[arg-type]
            message_thread_id=new_message.thread_id,
            business_connection_id=new_message.business_connection_id,
            reply_markup=new_message.reply_markup,
            parse_mode=new_message.parse_mode,
            link_preview_options=new_message.link_preview_options,
            message_effect_id=getattr(new_message, "message_effect_id", None),
        )

    async def send_media(self, bot: Bot, new_message: NewMessage) -> Message:
        method = getattr(bot, SEND_METHODS[new_message.media.type], None)  # type: ignore[union-attr]

        if not method:
            raise ValueError(
                f"ContentType {new_message.media.type} is not supported",  # type: ignore[union-attr]
            )

        return await method(
            new_message.chat.id,
            await self.get_media_source(new_message.media, bot),  # type: ignore[arg-type]
            message_thread_id=new_message.thread_id,
            business_connection_id=new_message.business_connection_id,
            caption=new_message.text,
            reply_markup=new_message.reply_markup,
            parse_mode=new_message.parse_mode,
            message_effect_id=getattr(new_message, "message_effect_id", None),
            **new_message.media.kwargs,  # type: ignore[union-attr]
        )