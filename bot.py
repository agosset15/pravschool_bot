import logging
import time
import os
from aiogram import executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from imports import dp, bot
import keyboards as kb
from db import Database
from web_edit.add_rasp import Exel

logging.basicConfig(level=logging.INFO)

db = Database("rs-bot.db", 'users.db')


############################
#       StatesGroup        #
############################
class Edit(StatesGroup):
    eday = State()
    etext = State()


class Admad(StatesGroup):
    ad = State()


class ClassWait(StatesGroup):
    clas = State()
    uch = State()
    chat_clas = State()


class KabWait(StatesGroup):
    kab = State()
    day = State()


class PaswdWait(StatesGroup):
    password = State()


class ExelWait(StatesGroup):
    file = State()
    rasp = State()
    tchr = State()
    kabs = State()


class AdminAdd(StatesGroup):
    id = State()
    name = State()
    uname = State()
    paswd = State()


zero = 0
b_zero = False
clases_list = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10б", "10г", "10ф", "11б", "11с", "11ф"]


@dp.message_handler(commands="start", state="*")
async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    global zero
    usr = db.user_exists(message.from_user.id)
    if usr is False:
        await message.answer("Вы у меня впервые!")
        if message.chat.type == 'group':
            await message.answer("Регистрация возможна только в личном чате с ботом")
        else:
            db.add_user(message.from_user.id, message.from_user.full_name, message.from_user.username, 0, None)
            await message.answer("Здравствуйте!\n\nЯ буду показывать вам расписание уроков Свято-Димитриевской школы.",
                                 reply_markup=kb.clases())
            await message.answer("Чтобы начать, выберете свой класс внизу экрана, "
                                 "или нажмите 'Я-учитель👨‍🏫' для перехода к учительскому расписанию.",
                                 reply_markup=kb.uchitel())
            await ClassWait.clas.set()
            print("Новый пользователь!")
    teachr = db.teacher(message.from_user.id)
    if teachr in range(1, 40):
        await message.answer("👨‍🏫", reply_markup=kb.get_startkeyboard())
        await message.answer(f"Вы учитель\.\nВыберете день, на который вы хотите увидеть расписание\."
                             f"\nВы можете выбрать расписание на неделю в ОСОБОМ МЕНЮ\."
                             f"\n[Книга отзывов и предложений](tg://resolve?domain=agosset15bot)",
                             reply_markup=kb.uinb(), parse_mode="MarkdownV2")
    elif teachr == 0:
        if db.is_chat(message.chat.id) is True:
            clas = db.chat(message.chat.id)
        else:
            clas = db.what_class(message.from_user.id)
        list_class = [101, 102, 103, 111, 112, 113]
        if clas in list_class:
            clas = int(clas / 10)
        await message.answer("👨‍🏫", reply_markup=kb.get_startkeyboard())
        await message.answer(f"Вы в {clas} классе\.\nВыберете день, на который вы хотите увидеть расписание\."
                             f"\nВы можете выбрать расписание на неделю в ОСОБОМ МЕНЮ\."
                             f"\n[Книга отзывов и предложений](tg://resolve?domain=agosset15bot)",
                             reply_markup=kb.inboard(), parse_mode="MarkdownV2")
    if message.from_user.id == 900645059:
        await message.answer("👑Ты в VIP-ке!", reply_markup=kb.vip_menu())
        print()
        print(f"Владелец вошел в приватку!")


@dp.message_handler(commands='stop', state="*")
async def stop(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("До свидания!", reply_markup=kb.rem())


@dp.message_handler(commands="admin")
async def cmd_admin(message: types.Message):
    adm = db.admin_exists(message.from_user.id)
    if adm is True:
        await message.answer("Напишите свой пароль:")
        await PaswdWait.password.set()
    else:
        await message.answer("Вас нет в списке админов.")


# Обработчик на текстовые команды
@dp.message_handler(content_types=['text'])
async def text(message: types.Message):
    class1 = db.what_class(message.from_user.id)
    dase = ["📕ПОНЕДЕЛЬНИК📕", "📗ВТОРНИК📗", "📘СРЕДА📘", "📙ЧЕТВЕРГ📙", "📔ПЯТНИЦА📔"]
    if class1 != 0:
        try:
            if db.is_chat(message.chat.id) is True:
                class1 = db.chat(message.chat.id)
            else:
                class1 = db.what_class(message.from_user.id)
            if message.text in dase:
                usersmessage = 0
                if message.text == "📕ПОНЕДЕЛЬНИК📕":
                    usersmessage = class1 + 0.1
                if message.text == "📗ВТОРНИК📗":
                    usersmessage = class1 + 0.2
                if message.text == "📘СРЕДА📘":
                    usersmessage = class1 + 0.3
                if message.text == "📙ЧЕТВЕРГ📙":
                    usersmessage = class1 + 0.4
                if message.text == "📔ПЯТНИЦА📔":
                    usersmessage = class1 + 0.5
                value = db.day(usersmessage)
                await message.answer(f"{message.text}:\n{value}", reply_markup=kb.get_startkeyboard())
            else:
                if message.text == "📖НА НЕДЕЛЮ📖":
                    value = db.week(class1)
                    await message.answer(f"✏️Понедельник:\n{value[0]}\n\n✏️Вторник:\n {value[1]}"
                                         f"\n\n✏️Среда:\n{value[2]}\n\n✏️Четверг:\n{value[3]}"
                                         f"\n\n✏️Пятница:\n{value[4]}",
                                         reply_markup=kb.get_startkeyboard())
        except TypeError or ValueError:
            await message.answer("Извините, сейчас расписание обновляется. Попробуйте еще раз через минутку.")
            print(message.from_user.id)
    else:
        try:
            if db.is_chat(message.chat.id) is True:
                class1 = int(db.chat(message.chat.id))
            else:
                class1 = int(db.what_class(message.from_user.id))
            if message.text in dase:
                usersmessage = 0
                if message.text == "📕ПОНЕДЕЛЬНИК📕":
                    usersmessage = class1 + 0.1
                if message.text == "📗ВТОРНИК📗":
                    usersmessage = class1 + 0.2
                if message.text == "📘СРЕДА📘":
                    usersmessage = class1 + 0.3
                if message.text == "📙ЧЕТВЕРГ📙":
                    usersmessage = class1 + 0.4
                if message.text == "📔ПЯТНИЦА📔":
                    usersmessage = class1 + 0.5
                value = db.teacher_rasp(usersmessage)
                await message.answer(f"{message.text}:\n{value}", reply_markup=kb.get_startkeyboard())
            if message.text == "📖НА НЕДЕЛЮ📖":
                clas = class1 + (1 / 10)
                value0 = db.teacher_rasp(clas)
                clas = class1 + (2 / 10)
                value1 = db.teacher_rasp(clas)
                clas = class1 + (3 / 10)
                value2 = db.teacher_rasp(clas)
                clas = class1 + (4 / 10)
                value3 = db.teacher_rasp(clas)
                clas = class1 + (5 / 10)
                value4 = db.teacher_rasp(clas)
                await message.answer(f"✏️Понедельник:\n{value0}\n\n✏️Вторник:\n {value1}\n\n✏️Среда:\n{value2}"
                                     f"\n\n✏️Четверг:\n{value3}\n\n✏️Пятница:\n{value4}",
                                     reply_markup=kb.get_startkeyboard())
        except TypeError or ValueError:
            await message.answer("Извините, сейчас расписание обновляется. Попробуйте еще раз через минутку.")
            print(message.from_user.id)
    if message.text == "📚ОСОБОЕ МЕНЮ📚":
        await message.answer("Вы перешли в особое меню.", reply_markup=kb.sp_menu())
    if message.text == "📚НА ГОД📚":
        await bot.send_photo(photo=open(f"photos/year.jpg", "rb"), caption="Вот расписание на год",
                             chat_id=message.from_user.id, reply_markup=kb.get_startkeyboard())
    if message.text == "⚙️Настройки⚙️":
        await message.answer("Вы перешли в меню настроек.", reply_markup=kb.settings())
    if message.text == "Изменить класс":
        await message.answer("Выберете класс, в котором учитесь.", reply_markup=kb.clases())
        await message.answer("Или нажмите на кнопку ниже, если вы учитель", reply_markup=kb.uchitel())
        await ClassWait.clas.set()
    if message.text == "меню отладки(для разработчика)":
        value = db.count()
        await message.answer(f"Всего пользователей: {value}\nНовых отзывов и предложений нет.",
                             reply_markup=kb.get_startkeyboard())


# Обработчик на callback-команды
@dp.callback_query_handler(lambda call: call.data, state="*")
async def call_handl(call: types.CallbackQuery, state: FSMContext):
    if call.data == "new_rasp":
        await call.message.answer("Пришлите пожалуйста файл с расширением .xlsx")
        await ExelWait.file.set()
    if call.data == "admin_add":
        await call.message.answer("Напишите id")
        await AdminAdd.id.set()
    if call.data == "edit":
        await call.message.answer("Введите номер дня.")
        await Edit.eday.set()
        await call.answer()
    if call.data == "ad":
        await bot.send_message(call.message.chat.id, text='Введите текст объявления.')
        await Admad.ad.set()
    if call.data == "uch":
        usersmessage = call.data
        await state.update_data(uch=usersmessage)
        global zero
        db.del_user(call.from_user.id)
        await bot.send_photo(photo=open(f"photos/tchrs.jpg", "rb"), caption="Введите свой номер из списка выше",
                             chat_id=call.from_user.id, reply_markup=kb.rem())
        await ClassWait.uch.set()
        await call.answer()
    if call.data == "now":
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
    if call.data == "tom":
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
    if call.data == "kab":
        await bot.send_photo(photo=open(f"photos/kabs.jpg", "rb"), caption="Введите номер кабинета из списка выше",
                             chat_id=call.from_user.id)
        await KabWait.kab.set()


@dp.message_handler(state=ClassWait.clas)
async def classadd(message: types.Message, state: FSMContext):
    class_list = ["10б", "10г", "10ф", "11б", "11с", "11ф"]
    if message.text == "/start":
        await state.finish()
    else:
        usersmessage = message.text
        if usersmessage in class_list:
            if usersmessage == "10б":
                usersmessage = "101"
            if usersmessage == "10г":
                usersmessage = "102"
            if usersmessage == "10ф":
                usersmessage = "103"
            if usersmessage == "11б":
                usersmessage = "111"
            if usersmessage == "11с":
                usersmessage = "112"
            if usersmessage == "11ф":
                usersmessage = "113"
        await state.update_data(clas=usersmessage)
        await state.finish()
        msg = int(usersmessage)
        db.del_user(message.from_user.id)
        db.add_user(message.from_user.id, message.from_user.first_name, message.from_user.username, msg, 0)
        await message.answer("""Вы всегда сможете изменить свой класс в меню "⚙️Настройки⚙️" в особом меню.""",
                             reply_markup=kb.get_startkeyboard())
        await message.answer("Выберете день, на который вы хотите увидеть расписание\."
                             "\nВы можете выбрать расписание на неделю в ОСОБОМ МЕНЮ\."
                             "\n[Книга отзывов и предложений](tg://resolve?domain=agosset15bot)",
                             reply_markup=kb.inboard(), parse_mode="MarkdownV2")


@dp.message_handler(state=ClassWait.uch)
async def uch(message: types.Message, state: FSMContext):
    if message.text == "/start" or message.text == "/stop":
        await state.finish()
    else:
        usersmessage = message.text
        msg = int(usersmessage)
        db.del_user(message.from_user.id)
        db.add_user(message.from_user.id, message.from_user.first_name, message.from_user.username, 0, msg)
        await state.update_data(uch=usersmessage)
        await state.finish()
        await message.answer("""Вы всегда сможете изменить свои данные в меню "⚙️Настройки⚙️" в особом меню.""",
                             reply_markup=kb.get_startkeyboard())
        await message.answer("Выберете день, на который вы хотите увидеть расписание\."
                             "\nВы можете выбрать расписание на неделю в ОСОБОМ МЕНЮ\."
                             "\n[Книга отзывов и предложений](tg://resolve?domain=agosset15bot)",
                             reply_markup=kb.uinb(), parse_mode="MarkdownV2")


@dp.message_handler(state=Edit.eday)
async def textadd(message: types.Message, state: FSMContext):
    usersmessage = float(message.text)
    await state.update_data(eday=usersmessage)
    await message.answer("Введите расписание.")
    await Edit.etext.set()


@dp.message_handler(state=KabWait.kab)
async def take_kab(message: types.Message, state: FSMContext):
    usersmessage = int(message.text)
    await state.update_data(kab=usersmessage)
    await message.answer("Введите день недели", reply_markup=kb.get_startkeyboard())
    await KabWait.day.set()


@dp.message_handler(state=KabWait.day)
async def get_kab_rasp(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    dase = ["📕ПОНЕДЕЛЬНИК📕", "📗ВТОРНИК📗", "📘СРЕДА📘", "📙ЧЕТВЕРГ📙", "📔ПЯТНИЦА📔"]
    if message.text in dase:
        usersmessage = message.text
        if usersmessage == "📕ПОНЕДЕЛЬНИК📕":
            usersmessage = 0.1
        if usersmessage == "📗ВТОРНИК📗":
            usersmessage = 0.2
        if usersmessage == "📘СРЕДА📘":
            usersmessage = 0.3
        if usersmessage == "📙ЧЕТВЕРГ📙":
            usersmessage = 0.4
        if usersmessage == "📔ПЯТНИЦА📔":
            usersmessage = 0.5
        await state.finish()

        kab1 = user_data['kab']
        id_day = kab1 + usersmessage
        value = db.kab(id_day)
        await message.answer(value)
    else:
        await state.finish()


# @dp.message_handler(state=Edit.etext)
# async def textadd2(message: types.Message, state: FSMContext):
# usersmessage = message.text
#  c
# day = user_data['eday']
# await state.finish()
# cursor.execute(f"SELECT * FROM rasp WHERE class = {day}")
#  rs = cursor.fetchone()
#  if not rs:
#     cursor.execute("INSERT INTO rasp values (:class, :rasp);", {
#         'class': day,
#         'rasp': usersmessage})
#      conn.commit()
# else:
#      cursor.execute(f"UPDATE rasp SET rasp = {usersmessage} WHERE class = ?", (day,))
#  await message.answer("Done!")


@dp.message_handler(state=Admad.ad)
async def getcount(message: types.Message, state: FSMContext):
    ad = message.text
    await state.update_data(ad=ad)
    await state.finish()
    userbase = db.ad()
    if len(userbase) > 1:
        for z in range(len(userbase)):
            await bot.send_message(userbase[z][0], text=f"Внимание!\n{ad}")
    else:
        await bot.send_message(userbase[0], f"Внимание!\n{ad}")
    await bot.send_message(message.chat.id, text='Done!')


@dp.message_handler(state=AdminAdd.id)
async def admin_id(message: types.Message, state: FSMContext):
    usersmessage = int(message.text)
    await state.update_data(id=usersmessage)
    await message.answer("Имя")
    await AdminAdd.name.set()


@dp.message_handler(state=AdminAdd.name)
async def admin_name(message: types.Message, state: FSMContext):
    usersmessage = message.text
    await state.update_data(name=usersmessage)
    await message.answer("Юзернейм, или None")
    await AdminAdd.uname.set()


@dp.message_handler(state=AdminAdd.uname)
async def admin_uname(message: types.Message, state: FSMContext):
    usersmessage = message.text
    await state.update_data(uname=usersmessage)
    await message.answer("Пароль")
    await AdminAdd.paswd.set()


@dp.message_handler(state=AdminAdd.paswd)
async def admin_pswd_set(message: types.Message, state: FSMContext):
    usersmessage = message.text
    await state.update_data(paswd=usersmessage)
    user_data = await state.get_data()
    await state.finish()
    db.add_admin(user_data['id'], user_data['name'], user_data['uname'], user_data['paswd'])
    await message.answer("Done!", reply_markup=kb.get_startkeyboard())


@dp.message_handler(state=PaswdWait.password)
async def admin_pswd(message: types.Message, state: FSMContext):
    usersmessage = message.text
    await state.update_data(password=usersmessage)
    await state.finish()
    psword = db.admin(message.from_user.id)
    if psword == usersmessage:
        await message.answer("Вы вошли в админку", reply_markup=kb.admin_menu())
    else:
        await message.answer("Неверно!", reply_markup=kb.get_startkeyboard())


@dp.message_handler(state="*", content_types=['document'])
async def admin_file(message: types.Message, state: FSMContext):
    prj_dir = os.path.abspath(os.path.curdir)
    name = f"{message.document.file_id}.xlsx"
    dest = f"{prj_dir}/xl_uploads/{name}"
    await state.update_data(file=name)
    db.delall()
    await message.document.download(destination_file=dest)
    await message.answer("Давайте разберемся с расписаниями."
                         "\nНапишите наименьший индекс строки с классным расписанием, и наибольший в формате: число1,"
                         "число2")
    await ExelWait.rasp.set()


@dp.message_handler(state=ExelWait.rasp)
async def admin_rasp(message: types.Message, state: FSMContext):
    prj_dir = os.path.abspath(os.path.curdir)
    usersmessage = message.text.split(',')
    data = await state.get_data()
    xl = Exel(data['file'], prj_dir)
    xl.rasp(int(usersmessage[0]), int(usersmessage[1]))
    await message.answer("Напишите количество учителей, наименьший индекс строки с учительским расписанием, "
                         "и наибольший в формате: количество,число1,число2")
    await ExelWait.tchr.set()


@dp.message_handler(state=ExelWait.tchr)
async def admin_rasp(message: types.Message, state: FSMContext):
    prj_dir = os.path.abspath(os.path.curdir)
    usersmessage = message.text.split(',')
    data = await state.get_data()
    xl = Exel(data['file'], prj_dir)
    xl.tchr_rasp(int(usersmessage[0]), int(usersmessage[1]), int(usersmessage[2]))
    await message.answer("Напишите количество кабинетов, наименьший индекс строки с расписанием по кабинетам, "
                         "и наибольший в формате: количество,число1,число2")
    await ExelWait.kabs.set()


@dp.message_handler(state=ExelWait.kabs)
async def admin_kab(message: types.Message, state: FSMContext):
    prj_dir = os.path.abspath(os.path.curdir)
    usersmessage = message.text.split(',')
    data = await state.get_data()
    xl = Exel(data['file'], prj_dir)
    xl.kab(int(usersmessage[0]), int(usersmessage[1]), int(usersmessage[2]))
    await message.answer("Готово!\nПодождите минутку,и новое расписание добавится в бота.")
    await state.finish()


@dp.inline_handler()
async def inline(query: types.InlineQuery):
    if query.query in clases_list:
        usersmessage = query.query
        if usersmessage == "10б":
            usersmessage = "101"
        if usersmessage == "10г":
            usersmessage = "102"
        if usersmessage == "10ф":
            usersmessage = "103"
        if usersmessage == "11б":
            usersmessage = "111"
        if usersmessage == "11с":
            usersmessage = "112"
        if usersmessage == "11ф":
            usersmessage = "113"
        await query.answer(kb.inline_kb(usersmessage), cache_time=1, is_personal=True,
                           switch_pm_text="Поговорить лично »»", switch_pm_parameter="ls")
    else:
        us = db.user_exists(query.from_user.id)
        if us is True:
            uh = db.teacher(query.from_user.id)
            cls = db.what_class(query.from_user.id)
            if cls != 0:
                await query.answer(kb.inline_kb(cls), cache_time=1, is_personal=True,
                                   switch_pm_text="Поговорить лично »»", switch_pm_parameter="ls")
            else:
                await query.answer(kb.inline_kb(clas=None, uch=uh), cache_time=1, is_personal=True,
                                   switch_pm_text="Поговорить лично »»", switch_pm_parameter="ls")
        else:
            buttons = [
                types.InlineQueryResultArticle(id="err", title="Вы не зарегистрированы!",
                                               description="Зарегистрируйтесь по кнопке выше, или напишите класс",
                                               input_message_content=types.InputTextMessageContent("Ошибка!"
                                                                                                   "\nВы не "
                                                                                                   "зарегистрированы. "
                                                                                                   "\n"
                                                                                                   "Зарегистрируйтесь "
                                                                                                   "в лс бота."))]
            await query.answer(buttons, cache_time=1, switch_pm_parameter="new", switch_pm_text="Регистрация »»")


@dp.message_handler(content_types=['new_chat_members'])
async def send_welcome(message: types.Message):
    bot_obj = await bot.get_me()
    bot_id = bot_obj.id

    for chat_member in message.new_chat_members:
        if chat_member.id == bot_id:
            await message.answer("Выберете класс в этом чате.", reply_markup=kb.clases())
            await ClassWait.chat_clas.set()


@dp.message_handler(state=ClassWait.chat_clas)
async def chat_class(message: types.Message, state: FSMContext):
    id1 = message.chat.id
    usersmessage = message.text
    class_list = ["10б", "10г", "10ф", "11б", "11с", "11ф"]
    if usersmessage in class_list:
        if usersmessage == "10б":
            usersmessage = "101"
        if usersmessage == "10г":
            usersmessage = "102"
        if usersmessage == "10ф":
            usersmessage = "103"
        if usersmessage == "11б":
            usersmessage = "111"
        if usersmessage == "11с":
            usersmessage = "112"
        if usersmessage == "11ф":
            usersmessage = "113"
        db.add_chat(id1, usersmessage)
    await message.answer("""Вы всегда сможете изменить класс в меню "⚙️Настройки⚙️" в особом меню.""",
                         reply_markup=kb.get_startkeyboard())
    await message.answer("Выберете день, на который вы хотите увидеть расписание\."
                         "\nВы можете выбрать расписание на неделю в ОСОБОМ МЕНЮ\."
                         "\n[Книга отзывов и предложений](tg://resolve?domain=agosset15bot)",
                         reply_markup=kb.inboard(), parse_mode="MarkdownV2")
    await state.finish()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
