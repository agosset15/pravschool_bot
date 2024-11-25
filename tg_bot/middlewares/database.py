from typing import Callable, Dict, Any, Awaitable, TypeVar

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, InlineQuery, ChatMemberUpdated

from tg_bot.models import DefaultService, User

M = TypeVar("M", Message, CallbackQuery, InlineQuery, ChatMemberUpdated)


class DatabaseMiddleware(BaseMiddleware):
    def __init__(self, db: DefaultService) -> None:
        self.db = db

    async def __call__(
            self,
            handler: Callable[[M, Dict[str, Any]], Awaitable[Any]],
            event: M,
            data: Dict[str, Any]
    ) -> Any:
        data['db'] = self.db
        data['user'] = await self.db.get_one(User, User.chat_id == event.from_user.id)
        result = await handler(event, data)
        return result
