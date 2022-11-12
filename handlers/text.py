from aiogram import Router
from aiogram.filters import Text
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from pravschool_bot.db import Database
from pravschool_bot.keyboards import keyboards as kb

router = Router()
db = Database("rs-bot.db", 'users.db')

days = ["ПОНЕДЕЛЬНИК", "ВТОРНИК", "СРЕДА", "ЧЕТВЕРГ", "ПЯТНИЦА"]


@router.message(Text("ОСОБОЕ МЕНЮ"))
@router.message(Text("НА НЕДЕЛЮ"))
@router.message(Text(days))
async def text(message: Message, state: FSMContext):
    await state.clear()
    if db.is_chat(message.chat.id) is True:
        try:
            class1 = db.chat(message.chat.id)
            if message.text in days:
                dase = {'ПОНЕДЕЛЬНИК': class1 + 0.1, 'ВТОРНИК': class1 + 0.2, 'СРЕДА': class1 + 0.3,
                        'ЧЕТВЕРГ': class1 + 0.4, 'ПЯТНИЦА': class1 + 0.5}
                usersmessage = dase[message.text]
                value = db.day(usersmessage)
                await message.answer(f"<b>{message.text}</b>:\n{value}", reply_markup=kb.get_startkeyboard(),
                                     parse_mode='HTML')
            else:
                if message.text == "НА НЕДЕЛЮ":
                    value = db.week(class1)
                    await message.answer(f"<b>Понедельник:</b>\n{value[0]}\n\n<b>Вторник:</b>\n{value[1]}"
                                         f"\n\n<b>Среда:</b>\n{value[2]}\n\n<b>Четверг:</b>\n{value[3]}"
                                         f"\n\n<b>Пятница:</b>\n{value[4]}",
                                         reply_markup=kb.get_startkeyboard(), parse_mode='HTML')
        except TypeError or ValueError:
            await message.answer("Извините, сейчас расписание обновляется. Попробуйте еще раз через минутку.")
            print(message.from_user.id)
            with open('error_log.txt', 'w+') as error_log:
                error_log.write(f"\n{message.from_user.id} - ошибка текст\учеников")
    else:
        class1 = db.what_class(message.from_user.id)
        if class1 != 0:
            try:
                if db.is_chat(message.chat.id) is True:
                    class1 = db.chat(message.chat.id)
                else:
                    class1 = db.what_class(message.from_user.id)
                if message.text in days:
                    dase = {'ПОНЕДЕЛЬНИК': class1 + 0.1, 'ВТОРНИК': class1 + 0.2, 'СРЕДА': class1 + 0.3,
                            'ЧЕТВЕРГ': class1 + 0.4, 'ПЯТНИЦА': class1 + 0.5}
                    usersmessage = dase[message.text]
                    value = db.day(usersmessage)
                    await message.answer(f"<b>{message.text}</b>:\n{value}", reply_markup=kb.get_startkeyboard(),
                                         parse_mode='HTML')
                else:
                    if message.text == "НА НЕДЕЛЮ":
                        value = db.week(class1)
                        await message.answer(f"<b>Понедельник:</b>\n{value[0]}\n\n<b>Вторник:</b>\n{value[1]}"
                                             f"\n\n<b>Среда:</b>\n{value[2]}\n\n<b>Четверг:</b>\n{value[3]}"
                                             f"\n\n<b>Пятница:</b>\n{value[4]}",
                                             reply_markup=kb.get_startkeyboard(), parse_mode='HTML')
            except TypeError or ValueError:
                await message.answer("Извините, сейчас расписание обновляется. Попробуйте еще раз через минутку.")
                print(message.from_user.id)
                with open('error_log.txt', 'w+') as error_log:
                    error_log.write(f"\n{message.from_user.id} - ошибка текст\учеников")
    if message.text == "ОСОБОЕ МЕНЮ":
        await message.answer("Вы перешли в особое меню.", reply_markup=kb.uinb())
