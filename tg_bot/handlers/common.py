from aiogram import Router, F
from aiogram.filters import Command
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, KICKED, MEMBER, ChatMemberUpdated
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from db.methods.create import create_student
from db.methods.get import get_all_students, get_student_by_telegram_id
from db.methods.update import update_student_nonblocked, update_student_blocked
from db.methods.delete import delete_student
from ..backend.notifications import get_duty
from ..keyboards import keyboards as kb
from ..config import *

router = Router()

zero = 0
clases_list = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10б", "10г", "10ф", "11б", "11с", "11ф"]


@router.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=KICKED)
)
async def user_blocked_bot(event: ChatMemberUpdated):
    update_student_blocked(event.from_user.id)


@router.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=MEMBER)
)
async def user_unblocked_bot(event: ChatMemberUpdated):
    update_student_nonblocked(event.from_user.id)


@router.message(NewUserFilter())
@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    global zero
    usr = get_student_by_telegram_id(message.from_user.id)
    code = kb.extract_unique_code(message.text)
    if usr is None:
        if code and code.split('_')[0] in clases_list:
            cod = code.split('_')[0]
            list1 = {'10г': '101', "10е": "102", '10ф': '103', '11г': '111', '11е': '112', '11ф': '113'}
            class_list = ["10г", "10е", "10ф", "11г", "11е", "11ф"]
            usersmessage = cod
            if usersmessage in class_list:
                usersmessage = list1[usersmessage]
            await message.answer("""Вы всегда сможете изменить свой класс в меню "Настройки" в особом меню.""",
                                 reply_markup=kb.get_startkeyboard())
            create_student(message.from_user.id, message.from_user.full_name, message.from_user.username, usersmessage,
                           code)
            await message.answer(f"Вы в {cod} классе.\nВыберете день, на который вы хотите увидеть расписание."
                                 f"\nВы можете выбрать расписание на неделю в ОСОБОМ МЕНЮ."
                                 f"\n{html.link('Книга отзывов и предложений', 'tg://resolve?domain=agosset15bot')}",
                                 reply_markup=kb.uinb(), parse_mode="HTML")
            print("Новый пользователь!")
            await bot.send_message(-1001845347264, f"{message.from_user.id} Новый пользователь!\n{code}")
        else:
            await message.answer("Вы у меня впервые!")
            if message.chat.type != 'private':
                await message.answer("Регистрация возможна только в личном чате с ботом\n")
            else:
                create_student(message.from_user.id, message.from_user.full_name, message.from_user.username, 0, code)
                await message.answer(
                    "Здравствуйте!\n\nЯ буду показывать вам расписание уроков Свято-Димитриевской школы.",
                    reply_markup=kb.clases())
                await message.answer("Чтобы начать, выберете свой класс внизу экрана, "
                                     "или нажмите 'Я-учитель👨‍🏫' для перехода к учительскому расписанию.",
                                     reply_markup=kb.uchitel())
                await state.set_state(ClassWait.clas)
                print("Новый пользователь!")
                await bot.send_message(-1001845347264, f"{message.from_user.id} Новый пользователь!\n{code}")
    else:
        if code == 'rereg':
            delete_student(message.from_user.id)
            await message.answer("Вы у меня впервые!")
            if message.chat.type != 'private':
                await message.answer("Регистрация возможна только в личном чате с ботом\n")
            else:
                create_student(message.from_user.id, message.from_user.full_name, message.from_user.username, 0, code)
                await message.answer(
                    "Здравствуйте!\n\nЯ буду показывать вам расписание уроков Свято-Димитриевской школы.",
                    reply_markup=kb.clases())
                await message.answer("Чтобы начать, выберете свой класс внизу экрана, "
                                     "или нажмите 'Я-учитель👨‍🏫' для перехода к учительскому расписанию.",
                                     reply_markup=kb.uchitel())
                await state.set_state(ClassWait.clas)
        else:
            if usr.isTeacher is True:
                await message.answer("👨‍🏫", reply_markup=kb.get_startkeyboard())
                await message.answer(f"Вы учитель\.\nВыберете день, на который вы хотите увидеть расписание\."
                                     f"\nВы можете выбрать расписание на неделю в ОСОБОМ МЕНЮ\."
                                     f"\n[Книга отзывов и предложений](tg://resolve?domain=agosset15bot)",
                                     reply_markup=kb.uinb(), parse_mode="MarkdownV2")
            else:
                clas = usr.clas
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
async def cmd_admin(message: Message):
    adm = get_student_by_telegram_id(message.from_user.id).isAdmin
    if adm is True:
        await message.answer("Вы уже админ. Вы можете добавлять домашнее задание.")
    else:
        await message.answer("Вы не админ, но можете им стать, для этого напишите @ag15bots")


@router.message(Command("duty"))
async def cmd_duty(message: Message, state: FSMContext):
    user = get_student_by_telegram_id(message.from_user.id)
    if user.isNs is True:
        if user.isParent is True:
            try:
                await ns.login(user.login, user.password, 1)
                stt = await ns.students()
                await ns.logout()
                await ns.logout()
                await ns.logout()
            except (SchoolNotFoundError, AuthError, NoResponseFromServer):
                await ns.logout()
                await message.answer("Ошибка!")
                return
            st = []
            for i in stt[0]:
                st.append(i['nickName'])
            await message.answer("Выберите ребенка:", reply_markup=kb.arr_kb(st))
            await state.set_state(GetDuty.child)
            return
        duty = await get_duty(user)
        if duty:
            await message.answer(duty, parse_mode="HTML", disable_web_page_preview=True)
        else:
            await message.answer("Ошибка!")
    else:
        await message.answer("У вас не введены данные ЭЖ. Вы можете сделать это в настройках.")


@router.callback_query(F.data == "users_check")
async def clb_usr(callback: CallbackQuery):
    userbase = get_all_students()
    message = "Пользователи:\nID    Класс    Имя    Реф\n\n"
    for z in userbase:
        message = message + f"{z.tgid}  {z.clas}  {z.name}    {z.ref}\n\n"
    if len(message) > 4096:
        for x in range(0, len(message), 4096):
            await callback.message.answer(message[x:x + 4096])
    else:
        await callback.message.answer(message, reply_markup=kb.sqlite_upd())
    await callback.answer()
