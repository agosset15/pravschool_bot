from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from tg_bot.models import User, DefaultService, Day
from tg_bot.config import ADMIN_ID, days
from tg_bot.keyboards import inline_kb, main_kb

router = Router()


@router.message(F.text == "Меню")
@router.message(F.text.in_(days))
async def text(message: Message, state: FSMContext, db: DefaultService, user: User, bot: Bot):
    await state.clear()
    if message.text == "Меню":
        return await message.answer("Вы перешли в меню.", reply_markup=main_kb())
    day: Day = await db.get_one(Day, Day.schedule_id == user.schedule, Day.name == message.text)
    if day is None:
        await message.answer("Ошибка! Нажмите /start")
        return await bot.send_message(ADMIN_ID, f"{message.from_user.id} - ошибка текст/учеников")
    await message.answer(f"<b>{message.text}</b>:\n{day.text}",
                         reply_markup=inline_kb(add_time="Посмотреть время"))
