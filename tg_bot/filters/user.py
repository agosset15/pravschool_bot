from aiogram.filters import BaseFilter
from aiogram.types import Message

from tg_bot.models import DefaultService, User


class NewUserFilter(BaseFilter):
    async def __call__(self, message: Message, db: DefaultService):
        user = await db.get_one(User, User.chat_id == message.from_user.id)
        return user is None
