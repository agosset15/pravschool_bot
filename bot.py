import sqlite3
import logging
import time
from aiogram import executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from imports import dp, bot
import keyboards as kb

logging.basicConfig(level=logging.INFO)


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
    napr = State()


#############################
#          SQLite           #
#############################
with sqlite3.connect("rs-bot.db") as conn:
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users0
    (id INTEGER, name VARCHAR, uname VARCHAR, class INTEGER, teacher BOOLEAN)
    """)

with sqlite3.connect("rs-bot.db") as conn:
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS uchitel_rasp
    (id_day INTEGER, rasp VARCHAR)
    """)

with sqlite3.connect("rs-bot.db") as conn:
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rasp
    (class INTEGER, rasp VARCHAR)
    """)

zero = 0
b_zero = False


@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    global zero
    cursor.execute(f"select * from users0 where id = {message.from_user.id}")
    usr = cursor.fetchone()
    if not usr:
        cursor.execute("INSERT INTO users0 values (:id, :name, :uname, :class, :teacher);",
                       {'id': message.from_user.id,
                        'name': message.from_user.first_name,
                        'uname': message.from_user.username,
                        'class': zero,
                        'teacher': None})
        conn.commit()
        await message.answer("Вы у меня впервые!")
    cursor.execute(f"select teacher from users0 where id = {message.from_user.id}")
    teachr = cursor.fetchone()[0]
    if teachr is None:
        await message.answer("Здраствуйте!\n\nЯ буду показывать вам расписание уроков Свято-Димитриевской школы.",
                             reply_markup=kb.clases())
        await message.answer("Чтобы начать, выберете свой класс внизу экрана, "
                             "или нажмите 'Я-учитель👨‍🏫' для перехода к учительскому расписанию.",
                             reply_markup=kb.uchitel())
        await ClassWait.clas.set()
    else:
        if teachr == True:
            await message.answer("Извините!\nУ разработчика бота нет расписания для учителей."
                                 "\nЕсли вы готовы посодействовать встройке этого расписания бота, то присылайте его "
                                 "на почту ag15@ag15.ru "
                                 "\n\nПока возможен только просмотр расписания классов.",
                                 reply_markup=kb.get_startkeyboard())
        else:
            cursor.execute(f"select class from users0 where id = {message.from_user.id}")
            clas = cursor.fetchone()[0]
            if clas == 101 or clas == 102 or clas == 103 or clas == 111 or clas == 112 or clas == 113:
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


# Обработчик на текстовые команды
@dp.message_handler(content_types=['text'])
async def text(message: types.Message):
    if message.text == "📕ПОНЕДЕЛЬНИК📕":
        class1 = cursor.execute("SELECT class FROM users0 WHERE id = ?", (message.from_user.id,)).fetchone()[0]
        clas1 = int(class1)
        clas = clas1 + 0.1
        value = cursor.execute("SELECT rasp FROM rasp WHERE class = ?", (clas,)).fetchone()[0]
        await message.answer(f"📕ПОНЕДЕЛЬНИК📕:\n{value}", reply_markup=kb.get_startkeyboard())
    if message.text == "📗ВТОРНИК📗":
        clas1 = cursor.execute("SELECT class FROM users0 WHERE id = ?", (message.from_user.id,)).fetchone()[0]
        clas = clas1 + 0.2
        value = cursor.execute("SELECT rasp FROM rasp WHERE class = ?", (clas,)).fetchone()[0]
        await message.answer(f"📗ВТОРНИК📗:\n{value}", reply_markup=kb.get_startkeyboard())
    if message.text == "📘СРЕДА📘":
        clas1 = cursor.execute("SELECT class FROM users0 WHERE id = ?", (message.from_user.id,)).fetchone()[0]
        clas = clas1 + 0.3
        value = cursor.execute("SELECT rasp FROM rasp WHERE class = ?", (clas,)).fetchone()[0]
        await message.answer(f"📘СРЕДА📘:\n{value}", reply_markup=kb.get_startkeyboard())
    if message.text == "📙ЧЕТВЕРГ📙":
        clas1 = cursor.execute("SELECT class FROM users0 WHERE id = ?", (message.from_user.id,)).fetchone()[0]
        clas = clas1 + 0.4
        value = cursor.execute("SELECT rasp FROM rasp WHERE class = ?", (clas,)).fetchone()[0]
        await message.answer(f"📙ЧЕТВЕРГ📙:\n{value}", reply_markup=kb.get_startkeyboard())
    if message.text == "📔ПЯТНИЦА📔":
        clas1 = cursor.execute("SELECT class FROM users0 WHERE id = ?", (message.from_user.id,)).fetchone()[0]
        clas = clas1 + 0.5
        value = cursor.execute("SELECT rasp FROM rasp WHERE class = ?", (clas,)).fetchone()[0]
        await message.answer(f"📔ПЯТНИЦА📔:\n{value}", reply_markup=kb.get_startkeyboard())
    if message.text == "📚ОСОБОЕ МЕНЮ📚":
        await message.answer("Вы перешли в особое меню.", reply_markup=kb.sp_menu())
    if message.text == "📚РАСПИСАНИЕ НА ГОД📚":
        # value = cursor.execute("SELECT rasp FROM rasp WHERE class = 1").fetchone()[0]
        await message.answer("Режим находится в разработке", reply_markup=kb.get_startkeyboard())
    if message.text == "📖РАСПИСАНИЕ НА НЕДЕЛЮ📖":
        clas1 = cursor.execute("SELECT class FROM users0 WHERE id = ?", (message.from_user.id,)).fetchone()[0]
        clas = clas1 + (1 / 10)
        value0 = cursor.execute("SELECT rasp FROM rasp WHERE class = ?", (clas,)).fetchone()[0]
        clas = clas1 + (2 / 10)
        value1 = cursor.execute("SELECT rasp FROM rasp WHERE class = ?", (clas,)).fetchone()[0]
        clas = clas1 + (3 / 10)
        value2 = cursor.execute("SELECT rasp FROM rasp WHERE class = ?", (clas,)).fetchone()[0]
        clas = clas1 + (4 / 10)
        value3 = cursor.execute("SELECT rasp FROM rasp WHERE class = ?", (clas,)).fetchone()[0]
        clas = clas1 + (5 / 10)
        value4 = cursor.execute("SELECT rasp FROM rasp WHERE class = ?", (clas,)).fetchone()[0]
        await message.answer(f"✏️Понедельник:\n{value0}\n\n✏️Вторник:\n {value1}\n\n✏️Среда:\n{value2}"
                             f"\n\n✏️Четверг:\n{value3}\n\n✏️Пятница:\n{value4}", reply_markup=kb.get_startkeyboard())
    if message.text == "⚙️Настройки⚙️":
        await message.answer("Вы перешли в меню настроек.", reply_markup=kb.settings())
    if message.text == "Изменить класс":
        await message.answer("Выберете класс, в котором учитесь.", reply_markup=kb.clases())
        await message.answer("Или нажмите на кнопку ниже, если вы учитель", reply_markup=kb.uchitel())
        await ClassWait.clas.set()
    if message.text == "меню отладки(для разработчика)":
        value = cursor.execute('SELECT Count(*) FROM users0').fetchone()[0]
        await message.answer(f"Всего пользователей: {value}\nНовых отзывов и предложений нет.",
                             reply_markup=kb.get_startkeyboard())


# Обработчик на callback-команды
@dp.callback_query_handler(lambda call: call.data, state="*")
async def call_handl(call: types.CallbackQuery, state: FSMContext):
    if call.data == "edit":
        await call.message.answer("Введите номер дня.")
        await Edit.eday.set()
    if call.data == "all_bots":
        await call.message.answer("Вот все наши боты:", reply_markup=kb.bots_list())
    if call.data == "ad":
        await bot.send_message(call.message.chat.id, text='Введите текст объявления.')
        await Admad.ad.set()
    if call.data == "uch":
        usersmessage = call.data
        await state.update_data(uch=usersmessage)
        global zero
        await state.finish()
        cursor.execute("DELETE from users0 where id = ?", (call.from_user.id,))
        cursor.execute("INSERT INTO users0 values (:id, :name, :uname, :class, :teacher);",
                       {'id': call.from_user.id,
                        'name': call.from_user.first_name,
                        'uname': call.from_user.username,
                        'class': zero,
                        'teacher': True})
        conn.commit()
        await call.message.answer("""Вы всегда сможете изменить свою роль в меню "⚙️Настройки⚙️" в особом меню.""",
                                  reply_markup=kb.get_startkeyboard())
        await call.message.answer("Выберете день, на который вы хотите увидеть расписание\."
                                  "\nВы можете выбрать расписание на неделю, и даже на год в ОСОБОМ МЕНЮ\."
                                  "\n[Книга отзывов и предложений](tg://resolve?domain=agosset15bot)",
                                  reply_markup=kb.inboard(), parse_mode="MarkdownV2")
    if call.data == "now":
        day = time.localtime()
        day = day.tm_wday + 1
        if day < 6:
            clas1 = cursor.execute("SELECT class FROM users0 WHERE id = ?", (call.from_user.id,)).fetchone()[0]
            clas = clas1 + (day / 10)
            value = cursor.execute("SELECT rasp FROM rasp WHERE class = ?", (clas,)).fetchone()[0]
            await call.message.answer(f"{value}")
        else:
            await call.message.answer("Сегодня выходной!")
    if call.data == "tom":
        day = time.localtime()
        day = day.tm_wday + 2
        userbase = [6, 7]
        if day < 6:
            clas1 = cursor.execute("SELECT class FROM users0 WHERE id = ?", (call.from_user.id,)).fetchone()[0]
            clas = clas1 + (day / 10)
            value = cursor.execute("SELECT rasp FROM rasp WHERE class = ?", (clas,)).fetchone()[0]
            await call.message.answer(f"{value}")
        if day == 8:
            clas1 = cursor.execute("SELECT class FROM users0 WHERE id = ?", (call.from_user.id,)).fetchone()[0]
            clas = clas1 + 0.1
            value = cursor.execute("SELECT rasp FROM rasp WHERE class = ?", (clas,)).fetchone()[0]
            await call.message.answer(f"{value}")
        if day in userbase:
            await call.message.answer("Завтра выходной!\nУра!")


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
                usersmessage = "101"
            if usersmessage == "11с":
                usersmessage = "102"
            if usersmessage == "11ф":
                usersmessage = "103"
        await state.update_data(clas=usersmessage)
        await state.finish()
        msg = int(usersmessage)
        cursor.execute("DELETE from users0 where id = ?", (message.from_user.id,))
        cursor.execute("INSERT INTO users0 values (:id, :name, :uname, :class, :teacher);",
                       {'id': message.from_user.id,
                        'name': message.from_user.first_name,
                        'uname': message.from_user.username,
                        'class': msg,
                        'teacher': False})
        conn.commit()
        await message.answer("""Вы всегда сможете изменить свой класс в меню "⚙️Настройки⚙️" в особом меню.""",
                             reply_markup=kb.get_startkeyboard())
        await message.answer("Выберете день, на который вы хотите увидеть расписание\."
                             "\nВы можете выбрать расписание на неделю в ОСОБОМ МЕНЮ\."
                             "\n[Книга отзывов и предложений](tg://resolve?domain=agosset15bot)",
                             reply_markup=kb.inboard(), parse_mode="MarkdownV2")


@dp.message_handler(state=Edit.eday)
async def textadd(message: types.Message, state: FSMContext):
    usersmessage = float(message.text)
    await state.update_data(eday=usersmessage)
    await message.answer("Введите расписание.")
    await Edit.etext.set()


@dp.message_handler(state=Edit.etext)
async def textadd2(message: types.Message, state: FSMContext):
    usersmessage = message.text
    await state.update_data(etext=usersmessage)
    user_data = await state.get_data()
    day = user_data['eday']
    await state.finish()
    cursor.execute(f"SELECT * FROM rasp WHERE class = {day}")
    rs = cursor.fetchone()
    if not rs:
        cursor.execute("INSERT INTO rasp values (:class, :rasp);", {
            'class': day,
            'rasp': usersmessage})
        conn.commit()
    else:
        cursor.execute(f"UPDATE rasp SET rasp = {usersmessage} WHERE class = ?", (day,))
    await message.answer("Done!")


@dp.message_handler(state=Admad.ad)
async def getcount(message: types.Message, state: FSMContext):
    ad = message.text
    await state.update_data(ad=ad)
    await state.finish()
    cursor.execute("SELECT id FROM users0")
    userbase = []
    while True:
        row = cursor.fetchone()
        if row is None:
            break
        userbase.append(row)
    if len(userbase) > 1:
        for z in range(len(userbase)):
            await bot.send_message(userbase[z][0], text=f"Внимание!\n{ad}")
    else:
        await bot.send_message(userbase[0], f"Внимание!\n{ad}")
    await bot.send_message(message.chat.id, text='Done!')


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
