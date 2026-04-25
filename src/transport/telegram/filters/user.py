from aiogram.filters import BaseFilter
from aiogram.types import Message

from src.core.dto import UserDto


class NewUserFilter(BaseFilter):
    async def __call__(self, message: Message, user: UserDto):
        return user.schedule_id is None