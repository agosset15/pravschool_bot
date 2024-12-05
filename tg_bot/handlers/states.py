from datetime import datetime, timedelta
from aiogram import Router, F, html, Bot
from aiogram.types import Message, CallbackQuery, InlineQuery
from aiogram.fsm.context import FSMContext

from tg_bot.states import GradeWait, RoomWait, NSLoginCredentialsWait, GetNS, NSChild, GetFreeRooms
from tg_bot.models import DefaultService, Schedule, User
from tg_bot.keyboards import start_kb, main_kb, inline_kb, settings_kb, ns_kb
from tg_bot.keyboards.inline import inline_schedule
from tg_bot.templates import main_text
from tg_bot.utils.ns import (get_ns_day, get_ns_object, NSError, NoResponseFromServer, encode_ns_password,
                             update_ns_object, AuthError, get_duty, DayNotFound)
from tg_bot.utils.rooms import find_free_rooms
from tg_bot.config import days, times

router = Router()


@router.message(GradeWait.grade)
async def grade_edit(message: Message, state: FSMContext, db: DefaultService, user: User):
    teacher = ("*teacher_" in message.text)
    grade = message.text
    if teacher:
        await message.delete()
        grade = message.text.strip("*teacher_")
        schedule = await db.get_one(Schedule, Schedule.id == int(grade), Schedule.entity == 1)
    else:
        schedule = await db.get_one(Schedule, Schedule.grade == grade, Schedule.entity == 0)
    if schedule is None:
        return await message.answer("Неверный ввод!\nДля отмены нажмите /start")
    await state.clear()
    await db.update(User, User.id == user.id, grade=schedule.grade, is_teacher=teacher, schedule=schedule.id)
    await message.answer("Вы всегда сможете изменить свой класс в меню настроек в особом меню.",
                         reply_markup=start_kb())
    user.grade = schedule.grade
    user.is_teacher = teacher
    await message.answer(main_text(user), reply_markup=main_kb())


@router.inline_query(GradeWait.grade, F.query.startswith("#teacher"))
async def grade_teacher(query: InlineQuery, db: DefaultService):
    name = query.query[9:]
    teachers = await db.get_all(Schedule, Schedule.entity == 1, Schedule.grade.icontains(name))
    await query.answer(inline_schedule(teachers, 'teacher'), is_personal=False, cache_time=86400)


@router.message(RoomWait.room, F.text.startswith("*room_"))
async def take_kab(message: Message, state: FSMContext, db: DefaultService):
    await message.delete()
    schedule: Schedule = await db.get_one(Schedule, Schedule.entity == 2, Schedule.id == int(message.text[6:]))
    if schedule is None:
        return await message.answer("Неверный ввод!\nДля отмены нажмите /start")
    await state.clear()
    values = [f"<b>{day.name}</b>:\n{day.text}" for day in schedule.days]
    await message.answer('\n\n'.join(values), reply_markup=inline_kb(add_time="Посмотреть время"))


@router.message(NSLoginCredentialsWait.login)
async def add_ns_login(message: Message, state: FSMContext):
    await state.update_data(login=message.text)
    await message.answer(f"Теперь пришлите свой пароль.\n"
                         f"Все пароли хранятся в боте в {html.underline('зашифрованном виде')} и никуда не передаются.")
    await state.set_state(NSLoginCredentialsWait.password)


@router.message(NSLoginCredentialsWait.password)
async def add_ns_login(message: Message, state: FSMContext, db: DefaultService, user: User):
    data = await state.get_data()
    try:
        ns = await get_ns_object(user)
        encoded_password = await encode_ns_password(ns, data['login'], message.text)
        await update_ns_object(user, ns)
    except AuthError as e:
        await message.answer(str(e))
        return await state.set_state(NSLoginCredentialsWait.login)
    await db.update(User, User.id == user.id, login=data['login'], password=encoded_password)
    if len(ns.students) > 1:
        await db.update(User, User.id == user.id, is_parent=True)
    await message.answer("Отлично, теперь вы можете настроить уведомления о просроченных заданиях, "
                         "а также получать информацию об актуальных.", reply_markup=main_kb())
    await state.clear()


@router.callback_query(F.data == "ns")
async def main_handler(call: CallbackQuery, state: FSMContext, user: User):
    if user.is_ns:
        start = datetime.now() - timedelta(days=datetime.now().weekday())
        end = start + timedelta(days=6)
        text = (f"Выберете день на который вы хотите посмотреть домашнее задание из электронного журнала\n"
                f"Текущая неделя: {start.strftime('%d.%m.%Y')} - {end.strftime('%d.%m.%Y')}")
        await state.set_state(GetNS.day)
        await state.update_data(start=start.strftime('%d.%m.%Y'), end=end.strftime('%d.%m.%Y'))
        if call.message.photo:
            await call.message.delete()
            return await call.message.answer(text, reply_markup=ns_kb())
        return await call.message.edit_text(text, reply_markup=ns_kb())
    else:
        return await call.answer("Вы не ввели свои данные. Введите их в меню настроек.", show_alert=True)


@router.callback_query(GetNS.day, F.data.endswith("_week"))
async def week(call: CallbackQuery, state: FSMContext):
    td = timedelta(days=7)
    if call.data == 'back_week':
        td = -td
    data = await state.get_data()
    start = datetime.strptime(data.get("start"), '%d.%m.%Y')
    end = datetime.strptime(data.get("end"), '%d.%m.%Y')
    start = (start + td).strftime('%d.%m.%Y')
    end = (end + td).strftime('%d.%m.%Y')
    await state.update_data(start=start, end=end)
    await call.message.edit_text(f"Выберете день на который вы хотите посмотреть домашнее задание из "
                                 f"электронного журнала\nТекущая неделя: {start} - {end}", reply_markup=ns_kb())


@router.callback_query(GetNS.day, F.data.in_([str(x) for x in range(len(days))]))
async def day_handler(call: CallbackQuery, state: FSMContext, user: User, bot: Bot):
    data = await state.get_data()
    start = datetime.strptime(data['start'], '%d.%m.%Y')
    day = int(call.data)
    try:
        ns = await get_ns_object(user)
        text = await get_ns_day(start, day, bot, ns)
    except NoResponseFromServer as e:
        return await call.message.edit_text(str(e),
                                            reply_markup=inline_kb(**{call.data: "Повторить попытку"}))
    except NSError as e:
        return await call.message.edit_text(str(e), reply_markup=settings_kb())
    except DayNotFound as e:
        if len(ns.students) > 1:
            await state.set_state(NSChild.day)
            await state.update_data(day=day, start=data['start'])
            await call.answer()
            return await call.message.answer(
                f"Для ребенка {ns.students[0]['nickName']}:\n\nВ этот день ничего нет.\n\nВыберите ребенка:",
                reply_markup=inline_kb(
                    **{str(i): child['nickName'] for i, child in enumerate(ns.students)}),
                disable_web_page_preview=True)
        return await call.answer(str(e), show_alert=True)
    await call.answer()
    if len(ns.students) > 1:
        await state.set_state(NSChild.day)
        await state.update_data(day=day, start=data['start'])
        return await call.message.answer(
            f"Для ребенка {ns.students[0]['nickName']}:\n\n" + text + '\n\nВыберите ребенка:',
            reply_markup=inline_kb(
                **{str(i): child['nickName'] for i, child in enumerate(ns.students)}),
            disable_web_page_preview=True)
    await state.clear()
    await call.message.answer(text, disable_web_page_preview=True)


@router.callback_query(NSChild.day)
async def get_ns_child(call: CallbackQuery, state: FSMContext, user: User, bot: Bot):
    data = await state.get_data()
    ns = await get_ns_object(user)
    start = datetime.strptime(data['start'], '%d.%m.%Y')
    day = int(data['day'])
    try:
        child_id = ns.students[int(call.data)]['studentId']
        text = await get_ns_day(start, day, bot, ns, child_id)
    except NoResponseFromServer as e:
        return await call.answer(str(e))
    except NSError as e:
        await call.message.delete()
        return await call.message.answer(str(e), reply_markup=settings_kb())
    except DayNotFound as e:
        return await call.answer(str(e), show_alert=True)
    await state.clear()
    await call.message.edit_text(text, disable_web_page_preview=True)


@router.callback_query(NSChild.duty)
async def get_duty_child(call: CallbackQuery, state: FSMContext, user: User, bot: Bot):
    ns = await get_ns_object(user)
    try:
        child_id = ns.students[int(call.data)]['studentId']
        text = await get_duty(bot, ns, child_id)
    except NoResponseFromServer as e:
        return await call.answer(str(e))
    except NSError as e:
        await call.message.delete()
        return await call.message.answer(str(e), reply_markup=settings_kb())
    await state.clear()
    await call.message.edit_text(text, disable_web_page_preview=True)


@router.callback_query(GetFreeRooms.day)
async def day_kabs_free(call: CallbackQuery, state: FSMContext, db: DefaultService):
    await state.clear()
    day = days[int(call.data)]
    rooms = await db.get_all(Schedule, Schedule.entity == 2)
    day_free_rooms = find_free_rooms(rooms)[int(call.data)]
    message_text = []
    for lesson_number, rooms in enumerate(day_free_rooms):
        message_text.append(f"{html.bold(lesson_number + 1)}({times[lesson_number]}):\n{', '.join(rooms)}")
    await call.message.edit_text(f"{day}, свободные кабинеты:\n\n"+'\n\n'.join(message_text), reply_markup=main_kb())
