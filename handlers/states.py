import os
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from pravschool_bot.web_edit.add_rasp import Exel
from pravschool_bot.db import Database
from pravschool_bot.keyboards import keyboards as kb
from pravschool_bot.config import *
from pravschool_bot.run import bot_send_message, bot

router = Router()
db = Database("rs-bot.db", 'users.db')


@router.message(ClassWait.clas)
async def classadd(message: Message, state: FSMContext):
    class_list = ["10б", "10г", "10ф", "11б", "11с", "11ф"]
    list1 = {'10б': '101', "10г": "102", '10ф': '103', '11б': '111', '11с': '112', '11ф': '113'}
    usersmessage = message.text
    if usersmessage in class_list:
        usersmessage = list1[usersmessage]
    await state.update_data(clas=usersmessage)
    await state.clear()
    msg = int(usersmessage)
    code = db.code(message.from_user.id)
    db.del_user(message.from_user.id)
    db.add_user(message.from_user.id, message.from_user.first_name, message.from_user.username, msg, 0, code)
    await message.answer("""Вы всегда сможете изменить свой класс в меню "⚙️Настройки⚙️" в особом меню.""",
                         reply_markup=kb.get_startkeyboard())
    await message.answer("Выберете день, на который вы хотите увидеть расписание\."
                         "\nВы можете выбрать расписание на неделю в ОСОБОМ МЕНЮ\."
                         "\n[Книга отзывов и предложений](tg://resolve?domain=agosset15bot)",
                         reply_markup=kb.uinb(), parse_mode="MarkdownV2")


@router.message(ClassWait.uch)
async def uch(message: Message, state: FSMContext):
    usersmessage = message.text
    msg = int(usersmessage)
    code = db.code(message.from_user.id)
    db.del_user(message.from_user.id)
    db.add_user(message.from_user.id, message.from_user.first_name, message.from_user.username, 0, msg, code)
    await state.update_data(uch=usersmessage)
    await state.clear()
    await message.answer("""Вы всегда сможете изменить свои данные в меню "⚙️Настройки⚙️" в особом меню.""",
                         reply_markup=kb.get_startkeyboard())
    await message.answer("Выберете день, на который вы хотите увидеть расписание\."
                         "\nВы можете выбрать расписание на неделю в ОСОБОМ МЕНЮ\."
                         "\n[Книга отзывов и предложений](tg://resolve?domain=agosset15bot)",
                         reply_markup=kb.uinb(), parse_mode="MarkdownV2")


@router.message(Edit.eday)
async def textadd(message: Message, state: FSMContext):
    usersmessage = float(message.text)
    await state.update_data(eday=usersmessage)
    await message.answer("Введите расписание.")
    await state.set_state(Edit.etext)


@router.message(KabWait.kab)
async def take_kab(message: Message, state: FSMContext):
    usersmessage = int(message.text)
    await state.update_data(kab=usersmessage)
    await message.answer("Введите день недели", reply_markup=kb.get_startkeyboard())
    await state.set_state(KabWait.day)


@router.message(KabWait.day)
async def get_kab_rasp(message: Message, state: FSMContext):
    user_data = await state.get_data()
    dase = ["ПОНЕДЕЛЬНИК", "ВТОРНИК", "СРЕДА", "ЧЕТВЕРГ", "ПЯТНИЦА"]
    dase1 = {"ПОНЕДЕЛЬНИК": 0.1, "ВТОРНИК": 0.2, "СРЕДА": 0.3, "ЧЕТВЕРГ": 0.4, "ПЯТНИЦА": 0.5}
    if message.text in dase:
        usersmessage = dase1[message.text]
        await state.clear()
        kab1 = user_data['kab']
        id_day = kab1 + usersmessage
        value = db.kab(id_day)
        await message.answer(value)
    else:
        await state.clear()


# @router.message(Edit.etext)
# async def textadd2(message: Message, state: FSMContext):
# usersmessage = message.text
#  c
# day = user_data['eday']
# await state.clear()
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


@router.message(Admad.ad)
async def getcount(message: Message, state: FSMContext):
    ad = message.text
    await state.update_data(ad=ad)
    await state.clear()
    userbase = db.ad()
    if len(userbase) > 1:
        for z in range(len(userbase)):
            await bot_send_message(chat_id=userbase[z][0], message_text=f"Внимание!\n{ad}")
    else:
        await bot_send_message(chat_id=userbase[0], message_text=f"Внимание!\n{ad}")
    await bot_send_message(chat_id=message.chat.id, message_text='Done!')


@router.message(AdminAdd.id)
async def admin_id(message: Message, state: FSMContext):
    usersmessage = int(message.text)
    await state.update_data(id=usersmessage)
    await message.answer("Имя")
    await state.set_state(AdminAdd.name)


@router.message(AdminAdd.name)
async def admin_name(message: Message, state: FSMContext):
    usersmessage = message.text
    await state.update_data(name=usersmessage)
    await message.answer("Юзернейм, или None")
    await state.set_state(AdminAdd.uname)


@router.message(AdminAdd.uname)
async def admin_uname(message: Message, state: FSMContext):
    usersmessage = message.text
    await state.update_data(uname=usersmessage)
    await message.answer("Пароль")
    await state.set_state(AdminAdd.paswd)


@router.message(AdminAdd.paswd)
async def admin_pswd_set(message: Message, state: FSMContext):
    usersmessage = message.text
    await state.update_data(paswd=usersmessage)
    user_data = await state.get_data()
    await state.clear()
    db.add_admin(user_data['id'], user_data['name'], user_data['uname'], user_data['paswd'])
    await message.answer("Done!", reply_markup=kb.get_startkeyboard())


@router.message(PaswdWait.password)
async def admin_pswd(message: Message, state: FSMContext):
    usersmessage = message.text
    await state.update_data(password=usersmessage)
    await state.clear()
    psword = db.admin(message.from_user.id)
    if psword == usersmessage:
        await message.answer("Вы вошли в админку", reply_markup=kb.admin_menu())
    else:
        await message.answer("Неверно!", reply_markup=kb.get_startkeyboard())


@router.message(F.document, ExelWait.file)
async def admin_file(message: Message, state: FSMContext):
    prj_dir = os.path.abspath(os.path.curdir)
    name = f"{message.document.file_id}.xlsx"
    dest = f"{prj_dir}/xl_uploads/{name}"
    await state.update_data(file=name)
    db.delall()
    d = message.document
    await bot.download(file=d, destination=dest)
    await message.answer("Давайте разберемся с расписаниями."
                         "\nНапишите наименьший индекс строки с классным расписанием, и наибольший в формате: число1,"
                         "число2")
    await state.set_state(ExelWait.rasp)


@router.message(ExelWait.file)
async def admin_file(message: Message):
    await message.answer("Это не распознано как документ, повторите попытку.")


@router.message(ExelWait.rasp)
async def admin_rasp(message: Message, state: FSMContext):
    prj_dir = os.path.abspath(os.path.curdir)
    usersmessage = message.text.split(',')
    data = await state.get_data()
    xl = Exel(data['file'], prj_dir)
    xl.rasp(int(usersmessage[0]), int(usersmessage[1]))
    await message.answer("Напишите количество учителей, наименьший индекс строки с учительским расписанием, "
                         "и наибольший в формате: количество,число1,число2")
    await state.set_state(ExelWait.tchr)


@router.message(ExelWait.tchr)
async def admin_rasp(message: Message, state: FSMContext):
    prj_dir = os.path.abspath(os.path.curdir)
    usersmessage = message.text.split(',')
    data = await state.get_data()
    xl = Exel(data['file'], prj_dir)
    xl.tchr_rasp(int(usersmessage[0]), int(usersmessage[1]), int(usersmessage[2]))
    await message.answer("Напишите количество кабинетов, наименьший индекс строки с расписанием по кабинетам, "
                         "и наибольший в формате: количество,число1,число2")
    await state.set_state(ExelWait.kabs)


@router.message(ExelWait.kabs)
async def admin_kab(message: Message, state: FSMContext):
    prj_dir = os.path.abspath(os.path.curdir)
    usersmessage = message.text.split(',')
    data = await state.get_data()
    xl = Exel(data['file'], prj_dir)
    xl.kab(int(usersmessage[0]), int(usersmessage[1]), int(usersmessage[2]))
    await message.answer("Готово!\nПодождите минутку,и новое расписание добавится в бота.")
    await state.clear()


@router.message(ClassWait.chat_clas)
async def chat_class(message: Message, state: FSMContext):
    id1 = message.chat.id
    usersmessage = message.text
    class_list = ["10б", "10г", "10ф", "11б", "11с", "11ф"]
    if usersmessage in class_list:
        if usersmessage == "10б":
            usersmessage = 101
        if usersmessage == "10г":
            usersmessage = 102
        if usersmessage == "10ф":
            usersmessage = 103
        if usersmessage == "11б":
            usersmessage = 111
        if usersmessage == "11с":
            usersmessage = 112
        if usersmessage == "11ф":
            usersmessage = 113
        db.add_chat(id1, usersmessage)
    await message.answer("""Вы всегда сможете изменить класс в меню "⚙️Настройки⚙️" в особом меню.""",
                         reply_markup=kb.get_startkeyboard())
    await message.answer("Выберете день, на который вы хотите увидеть расписание\."
                         "\nВы можете выбрать расписание на неделю в ОСОБОМ МЕНЮ\."
                         "\n[Книга отзывов и предложений](tg://resolve?domain=agosset15bot)",
                         reply_markup=kb.uinb(), parse_mode="MarkdownV2")
    await state.clear()


@router.message(F.photo, PhotoAdd.kabs)
async def photoadd_kabs(message: Message, state: FSMContext):
    print(message.photo[-1].file_id)
    await state.update_data(kabs=message.photo[-1].file_id)
    await message.answer("Пришлите фото tchrs")
    await state.set_state(PhotoAdd.tchrs)


@router.message(F.photo, PhotoAdd.tchrs)
async def photoadd_tchrs(message: Message, state: FSMContext):
    print(message.photo[-1].file_id)
    await state.update_data(tchrs=message.photo[-1].file_id)
    await message.answer("Пришлите фото year")
    await state.set_state(PhotoAdd.year)


@router.message(F.photo, PhotoAdd.year)
async def photoadd_year(message: Message, state: FSMContext):
    print(message.photo[-1].file_id)
    data = await state.get_data()
    a = [data['kabs'], data['tchrs'], message.photo[-1].file_id]
    with open('ids.txt', 'w') as txt:
        txt.write(f"{a}")
    await message.answer("Получилось!")
    await state.clear()


@router.message(DelUser.id)
async def deluser_id(message: Message, state: FSMContext):
    db.delete(int(message.text))
    await message.answer("Получилось!", reply_markup=kb.uinb())
