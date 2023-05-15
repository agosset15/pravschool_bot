import ast
from aiogram import Router
from aiogram.filters import Text
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from ...db.methods.get import get_student_by_telegram_id, get_schedule, get_teacher_schedule
from ..keyboards import keyboards as kb
from ..config import bot

router = Router()

days = ["ПОНЕДЕЛЬНИК", "ВТОРНИК", "СРЕДА", "ЧЕТВЕРГ", "ПЯТНИЦА"]
admin_id = 900645059


@router.message(Text("ОСОБОЕ МЕНЮ"))
@router.message(Text(days))
async def text(message: Message, state: FSMContext):
    await state.clear()
    usr = get_student_by_telegram_id(message.from_user.id)
    clas = usr.clas
    if message.text in days:
        if usr.isTeacher == 0:
            try:
                dase = {'ПОНЕДЕЛЬНИК': 1, 'ВТОРНИК': 2, 'СРЕДА': 3,
                        'ЧЕТВЕРГ': 4, 'ПЯТНИЦА': 5}
                usersmessage = dase[message.text]
                value = ast.literal_eval(get_schedule(clas, usersmessage))
                value = '\n'.join(value)
                await message.answer(f"<b>{message.text}</b>:\n{value}", reply_markup=kb.get_startkeyboard(),
                                     parse_mode='HTML')
            except TypeError or ValueError:
                await message.answer("Извините, сейчас расписание обновляется. Попробуйте еще раз через минутку.")
                await bot.send_message(admin_id, f"{message.from_user.id} - ошибка текст\учеников")
                print(message.from_user.id)
                await bot.send_message(-1001845347264, f"{message.from_user.id} ошибка текст\учеников")
        elif usr.isTeacher == 1:
            try:
                dase = {'ПОНЕДЕЛЬНИК': 1, 'ВТОРНИК': 2, 'СРЕДА': 3,
                        'ЧЕТВЕРГ': 4, 'ПЯТНИЦА': 5}
                usersmessage = dase[message.text]
                value = ast.literal_eval(get_teacher_schedule(clas, usersmessage))
                value = '\n'.join(value)
                await message.answer(f"<b>{message.text}</b>:\n{value}", reply_markup=kb.get_startkeyboard(),
                                     parse_mode='HTML')
            except TypeError or ValueError:
                await message.answer("Извините, сейчас расписание обновляется. Попробуйте еще раз через минутку.")
                await bot.send_message(admin_id, f"{message.from_user.id} - ошибка текст\учителей")
                print(message.from_user.id)
                await bot.send_message(-1001845347264, f"{message.from_user.id} ошибка текст\учителей")
    elif message.text == "ОСОБОЕ МЕНЮ":
        await message.answer("Вы перешли в особое меню.", reply_markup=kb.uinb())
