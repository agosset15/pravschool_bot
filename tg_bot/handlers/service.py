from aiogram import Router
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, KICKED, MEMBER, ChatMemberUpdated

from tg_bot.models import User, DefaultService

router = Router()


@router.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=KICKED)
)
async def user_blocked_bot(event: ChatMemberUpdated, db: DefaultService):
    await db.update(User, User.chat_id == event.from_user.id, blocked=True)


@router.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=MEMBER)
)
async def user_unblocked_bot(event: ChatMemberUpdated, db: DefaultService):
    await db.update(User, User.chat_id == event.from_user.id, blocked=False)
