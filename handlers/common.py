from aiogram import Router, F
from aiogram.filters import Command, Text
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, JOIN_TRANSITION
from pravschool_bot.db import Database
from pravschool_bot.keyboards import keyboards as kb
from pravschool_bot.config import *

router = Router()
db = Database("rs-bot.db", 'users.db')

zero = 0
clases_list = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10б", "10г", "10ф", "11б", "11с", "11ф"]


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    global zero
    usr = db.user_exists(message.from_user.id)
    code = kb.extract_unique_code(message.text)
    if usr is False:
        if code and code.split('_')[0] in clases_list:
            cod = code.split('_')[0]
            list1 = {'10б': '101', "10г": "102", '10ф': '103', '11б': '111', '11с': '112', '11ф': '113'}
            class_list = ["10б", "10г", "10ф", "11б", "11с", "11ф"]
            usersmessage = cod
            if usersmessage in class_list:
                usersmessage = list1[usersmessage]
            await message.answer("""Вы всегда сможете изменить свой класс в меню "Настройки" в особом меню.""",
                                 reply_markup=kb.get_startkeyboard())
            db.add_user(message.from_user.id, message.from_user.full_name, message.from_user.username, usersmessage,
                        None, code)
            await message.answer(f"Вы в {cod} классе\.\nВыберете день, на который вы хотите увидеть расписание\."
                                 f"\nВы можете выбрать расписание на неделю в ОСОБОМ МЕНЮ\."
                                 f"\n[Книга отзывов и предложений](tg://resolve?domain=agosset15bot)",
                                 reply_markup=kb.uinb(), parse_mode="MarkdownV2")
            print("Новый пользователь!")
            with open('error_log.txt', 'w+') as error_log:
                txt = error_log.read()
                error_log.write(f"{txt}\nНовый пользователь!")
        else:
            await message.answer("Вы у меня впервые!")
            if message.chat.type == 'group':
                await message.answer("Регистрация возможна только в личном чате с ботом")
            else:
                db.add_user(message.from_user.id, message.from_user.full_name, message.from_user.username, 0, None,
                            code)
                await message.answer(
                    "Здравствуйте!\n\nЯ буду показывать вам расписание уроков Свято-Димитриевской школы.",
                    reply_markup=kb.clases())
                await message.answer("Чтобы начать, выберете свой класс внизу экрана, "
                                     "или нажмите 'Я-учитель👨‍🏫' для перехода к учительскому расписанию.",
                                     reply_markup=kb.uchitel())
                await state.set_state(ClassWait.clas)
                print("Новый пользователь!")
                with open('error_log.txt', 'w+') as error_log:
                    txt = error_log.read()
                    error_log.write(f"{txt}\nНовый пользователь!")
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
                             reply_markup=kb.uinb(), parse_mode="MarkdownV2")
    if message.from_user.id == 900645059:
        await message.answer("👑Ты в VIP-ке!", reply_markup=kb.vip_menu())
        print()
        print(f"Владелец вошел в приватку!")


@router.message(Command("stop"))
async def stop(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("До свидания!", reply_markup=kb.rem())


@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    adm = db.admin_exists(message.from_user.id)
    if adm is True:
        await message.answer("Напишите свой пароль:")
        await state.set_state(PaswdWait.password)
    else:
        await message.answer("Вас нет в списке админов.")


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION),
                       F.chat.type.in_({"group", "supergroup"}))
async def send_welcome(message: Message, state: FSMContext):
    await message.answer("Выберете класс в этом чате.", reply_markup=kb.clases())
    await state.set_state(ClassWait.chat_clas)


@router.callback_query(Text("log"))
async def clb_log(callback: CallbackQuery):
    with open('error_log.txt', 'r') as error_log:
        message = f"Вот лог:\n{error_log.read()}"
    if len(message) > 4096:
        for x in range(0, len(message), 4096):
            await callback.message.answer(message[x:x + 4096])
    else:
        await callback.message.answer(message)
    await callback.answer()


@router.callback_query(Text("users_check"))
async def clb_usr(callback: CallbackQuery):
    userbase = db.ad()
    message = "Пользователи:\nID    Класс    Имя    Реф\n\n"
    for z in userbase:
        message = message + f"{z[0]}  {db.what_class(z[0])}  {db.what_name(z[0])}    {db.code(z[0])}\n\n"
    if len(message) > 4096:
        for x in range(0, len(message), 4096):
            await callback.message.answer(message[x:x + 4096])
    else:
        await callback.message.answer(message)
    await callback.answer()
