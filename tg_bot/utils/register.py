from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from tg_bot.models import DefaultService, User
from tg_bot.keyboards.common import grades
from tg_bot.keyboards import inline_kb
from tg_bot.states.user import GradeWait
from tg_bot.config import LOG_CHAT


async def register(message: Message, state: FSMContext, bot: Bot, db: DefaultService, code: str):
    if message.chat.type != 'private':
        await message.answer("Регистрация возможна только в личном чате с ботом\n")
        return
    await db.create(User, chat_id=message.from_user.id, name=message.from_user.full_name,
                    username=message.from_user.username, ref=code)
    await message.answer(
        "Здравствуйте!\n\nЯ буду показывать вам расписание уроков Свято-Димитриевской школы.",
        reply_markup=grades())
    await message.answer("Чтобы начать, выберете свой класс внизу экрана, "
                         "или нажмите 'Я-учитель👨‍🏫' для перехода к учительскому расписанию.",
                         reply_markup=inline_kb(uch="Я-учитель👨‍🏫"))
    await state.set_state(GradeWait.grade)
    await bot.send_message(LOG_CHAT, f"{message.from_user.id} Новый пользователь!\n{code}")


def extract_unique_code(text):
    return text.split()[1] if len(text.split()) > 1 else None
