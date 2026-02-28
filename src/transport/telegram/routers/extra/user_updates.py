from typing import Optional

from aiogram import Router
from aiogram.filters import JOIN_TRANSITION, LEAVE_TRANSITION, ChatMemberUpdatedFilter
from aiogram.types import ChatMemberUpdated
from dishka import FromDishka

from src.core.dto import UserDto
from src.services.user import UserService

# For only ChatType.PRIVATE (app/bot/filters/private.py)

router = Router(name=__name__)


@router.my_chat_member(ChatMemberUpdatedFilter(JOIN_TRANSITION))
async def on_unblocked(
    member: ChatMemberUpdated,
    user: Optional[UserDto],
    user_service: FromDishka[UserService],
) -> None:
    if not user:
        return

    await user_service.set_block(user, False)


@router.my_chat_member(ChatMemberUpdatedFilter(LEAVE_TRANSITION))
async def on_blocked(
    member: ChatMemberUpdated,
    user: Optional[UserDto],
    user_service: FromDishka[UserService],
) -> None:
    if not user:
        return

    await user_service.set_block(user, True)