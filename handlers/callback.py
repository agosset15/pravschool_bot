import time
from aiogram import Router
from aiogram.filters import Text
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from pravschool_bot.db import Database
from pravschool_bot.keyboards import keyboards as kb
from pravschool_bot.config import *

router = Router()

db = Database("rs-bot.db", 'users.db')
sp = ["year", "settings", "change_class", "info", "back", "delete", "del_user"]


@router.callback_query(Text(sp))
async def special(call: CallbackQuery, state: FSMContext):
    if call.data == "year":
        await call.message.delete()
        with open("ids.txt", "r") as text_id:
            photo_id = text_id.read()
        photo_id = photo_id.strip("[]").split(',')[2].strip(" ''")
        await call.message.answer_photo(photo_id, caption="Вот расписание на год", reply_markup=kb.uinb())
        await call.answer()
    if call.data == "settings":
        await call.message.delete()
        await call.message.answer("Вы перешли в меню настроек.", reply_markup=kb.settings())
        await call.answer()
    if call.data == "change_class":
        await call.message.answer("Выберете класс, в котором учитесь.", reply_markup=kb.clases())
        await call.message.answer("Или нажмите на кнопку ниже, если вы учитель", reply_markup=kb.uchitel())
        await state.set_state(ClassWait.clas)
        await call.answer()
    if call.data == "info":
        await call.message.delete()
        value = db.count()
        await call.message.answer(f"Всего пользователей: {value}\nНовых отзывов и предложений нет.",
                                  reply_markup=kb.settings())
        await call.answer()
    if call.data == "back":
        await call.message.delete()
        await call.message.answer("Вы вернулись в главное меню.", reply_markup=kb.uinb())
        await call.answer()
    if call.data == "delete":
        db.delete(call.from_user.id)
        await call.message.answer("Вы успешно удалены из базы данных бота.\nПожалуйста, нажмите /start для продолжения.",
                                  reply_markup=kb.rem())
        await call.answer()
    if call.data == "del_user":
        await call.message.answer("Введите id пользователя")
        await state.set_state(DelUser.id)


@router.callback_query(Text("now"))
async def call_now(call: CallbackQuery):
    try:
        class1 = db.what_class(call.from_user.id)
        if class1 != 0:
            if db.is_chat(call.message.chat.id) is True:
                class1 = db.chat(call.message.chat.id)
            else:
                class1 = db.what_class(call.from_user.id)
            day = time.localtime()
            day = day.tm_wday + 1
            if day < 6:
                clas = class1 + (day / 10)
                value = db.day(clas)
                await call.message.answer(f"{value}")
            else:
                await call.message.answer("Сегодня выходной!")
            await call.answer()
        else:
            day = time.localtime()
            day = day.tm_wday + 1
            if day < 6:
                if db.is_chat(call.message.chat.id) is True:
                    class1 = db.chat(call.message.chat.id)
                else:
                    class1 = db.what_class(call.from_user.id)
                clas = class1 + (day / 10)
                value = db.teacher_rasp(clas)
                await call.message.answer(f"{value}")
            else:
                await call.message.answer("Сегодня выходной!")
            await call.answer()
    except TypeError or ValueError:
        await call.message.answer("Извините, сейчас расписание обновляется. Попробуйте еще раз через минутку.")
        print(call.from_user.id)
        with open('error_log.txt', 'w+') as error_log:
            txt = error_log.read()
            error_log.write(f"{txt}\n{call.from_user.id} - ошибка колл\сегодня")


@router.callback_query(Text("tom"))
async def call_tom(call: CallbackQuery):
    try:
        class1 = db.what_class(call.from_user.id)
        if class1 != 0:
            if db.is_chat(call.message.chat.id) is True:
                class1 = db.chat(call.message.chat.id)
            else:
                class1 = db.what_class(call.from_user.id)
            day = time.localtime()
            day = day.tm_wday + 2
            userbase = [6, 7]
            if day < 6:
                clas = class1 + (day / 10)
                value = db.day(clas)
                await call.message.answer(f"{value}")
            elif day == 8:
                clas = class1 + 0.1
                value = db.day(clas)
                await call.message.answer(f"{value}")
            elif day in userbase:
                await call.message.answer("Завтра выходной!\nУра!")
            await call.answer()
        else:
            day = time.localtime()
            day = day.tm_wday + 2
            userbase = [6, 7]
            clas1 = db.teacher(call.from_user.id)
            if day < 6:
                clas = clas1 + (day / 10)
                value = db.teacher_rasp(clas)
                await call.message.answer(f"{value}")
            elif day == 8:
                clas = clas1 + 0.1
                value = db.teacher_rasp(clas)
                await call.message.answer(f"{value}")
            elif day in userbase:
                await call.message.answer("Завтра выходной!\nУра!")
            await call.answer()
    except TypeError or ValueError:
        await call.message.answer("Извините, сейчас расписание обновляется. Попробуйте еще раз через минутку.")
        print(call.from_user.id)
        with open('error_log.txt', 'w+') as error_log:
            txt = error_log.read()
            error_log.write(f"{txt}\n{call.from_user.id} - ошибка колл\завтра")


@router.callback_query(Text(["new_rasp", "admin_add", "edit", "ad", "uch", "kab", "photo_add"]))
async def other_call(call: CallbackQuery, state: FSMContext):
    if call.data == "new_rasp":
        await call.message.answer("Пришлите пожалуйста файл с расширением .xlsx")
        await state.set_state(ExelWait.file)
        await call.answer()
    if call.data == "admin_add":
        await call.message.answer("Напишите id")
        await state.set_state(AdminAdd.id)
        await call.answer()
    if call.data == "edit":
        await call.message.answer("Введите номер дня.")
        await state.set_state(Edit.eday)
        await call.answer()
    if call.data == "ad":
        await call.message.answer('Введите текст объявления.')
        await state.set_state(Admad.ad)
        await call.answer()
    if call.data == "uch":
        usersmessage = call.data
        await state.update_data(uch=usersmessage)
        db.del_user(call.from_user.id)
        with open("ids.txt", "r") as text_id:
            photo_id = text_id.read()
        photo_id = photo_id.strip("[]").split(',')[1].strip(" ''")
        await call.message.answer_photo(photo_id, caption="Введите свой номер из списка выше",
                                        reply_markup=kb.rem())
        await state.set_state(ClassWait.uch)
        await call.answer()
    if call.data == "kab":
        with open("ids.txt", "r") as text_id:
            photo_id = text_id.read()
        photo_id = photo_id.strip("[]").split(',')[0].strip(" ''")
        await call.message.answer_photo(photo_id, caption="Введите номер кабинета из списка выше",
                                        reply_markup=kb.rem())
        await state.set_state(KabWait.kab)
        await call.answer()
    if call.data == "photo_add":
        await call.message.answer("Пришлите фото kabs")
        await state.set_state(PhotoAdd.kabs)
        await call.answer()
