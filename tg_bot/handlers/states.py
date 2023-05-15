from datetime import datetime, timedelta
import os
import ast
from aiogram import Router, F, html
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError, TelegramNotFound
from netschoolapi.errors import SchoolNotFoundError, AuthError

from ..backend.add_rasp import Exel
from db.methods.update import (edit_student_clas, switch_student_admin, edit_student_login, edit_student_password,
                               edit_homework, edit_homework_upd_date, switch_student_ns, switch_student_teasher_false,
                               switch_student_teasher_true, update_student_blocked, update_student_nonblocked)
from db.methods.create import create_homework
from db.methods.get import get_kab_schedule, get_all_students, get_student_by_telegram_id, get_homework
from db.methods.delete import delete_schedules, delete_student
from ..keyboards import keyboards as kb
from ..config import *

router = Router()

days = ["📕ПОНЕДЕЛЬНИК📕", "📗ВТОРНИК📗", "📘СРЕДА📘", "📙ЧЕТВЕРГ📙", "📔ПЯТНИЦА📔"]


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
    edit_student_clas(message.from_user.id, msg)
    switch_student_teasher_false(message.from_user.id)
    await message.answer("""Вы всегда сможете изменить свой класс в меню настроек в особом меню.""",
                         reply_markup=kb.get_startkeyboard())
    await message.answer("Выберете день, на который вы хотите увидеть расписание\."
                         "\nВы можете выбрать расписание на неделю в ОСОБОМ МЕНЮ\."
                         "\n[Книга отзывов и предложений](tg://resolve?domain=agosset15bot)",
                         reply_markup=kb.uinb(), parse_mode="MarkdownV2")


@router.message(ClassWait.uch)
async def uch(message: Message, state: FSMContext):
    usersmessage = message.text
    msg = int(usersmessage)
    edit_student_clas(message.from_user.id, msg)
    switch_student_teasher_true(message.from_user.id)
    await state.update_data(uch=usersmessage)
    await state.clear()
    await message.answer("""Вы всегда сможете изменить свои данные в меню настроек в особом меню.""",
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
    value = []
    for i in range(1, 6):
        value.append('\n'.join(ast.literal_eval(get_kab_schedule(usersmessage, i))))
    await message.answer(f"<b>Понедельник:</b>\n{value[0]}\n\n<b>Вторник:</b>\n{value[1]}"
                         f"\n\n<b>Среда:</b>\n{value[2]}\n\n<b>Четверг:</b>\n{value[3]}"
                         f"\n\n<b>Пятница:</b>\n{value[4]}",
                         reply_markup=kb.get_startkeyboard(), parse_mode='HTML')
    await state.clear()


@router.message(Admad.ad)
async def getcount(message: Message, state: FSMContext):
    ad = message.text
    await state.update_data(ad=ad)
    await state.clear()
    userbase = get_all_students()
    if len(userbase) > 1:
        for z in userbase:
            try:
                await bot.send_message(z.id, f"Внимание!\n{ad}")
            except TelegramBadRequest or TelegramForbiddenError or TelegramNotFound:
                update_student_blocked(z.id)
                pass
    else:
        await bot.send_message(userbase[0].id, f"Внимание!\n{ad}")
    await bot.send_message(message.chat.id, 'Done!')


@router.message(AdminAdd.id)
async def admin_pswd_set(message: Message, state: FSMContext):
    await state.clear()
    switch_student_admin(int(message.text))
    await message.answer("Done!", reply_markup=kb.get_startkeyboard())


@router.message(F.document, ExelWait.file)
async def admin_file(message: Message, state: FSMContext):
    prj_dir = os.path.abspath(os.path.curdir)
    name = f"{message.document.file_id}.xlsx"
    dest = f"{prj_dir}/tg_bot/xl_uploads/{name}"
    await state.update_data(file=name)
    delete_schedules()
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
    await id_ad(a)
    await message.answer("Получилось!")
    await state.clear()


@router.message(DelUser.id)
async def deluser_id(message: Message, state: FSMContext):
    delete_student(int(message.text))
    await message.answer("Получилось!", reply_markup=kb.uinb())
    await state.clear()


@router.message(AddNS.login)
async def add_ns_login(message: Message, state: FSMContext):
    await state.update_data(login=message.text)
    await message.answer("Теперь пришлите свой пароль")
    await state.set_state(AddNS.password)


@router.message(AddNS.password)
async def add_ns_login(message: Message, state: FSMContext):
    data = await state.get_data()
    edit_student_login(message.from_user.id, data['login'])
    edit_student_password(message.from_user.id, message.text)
    switch_student_ns(message.from_user.id)
    await message.answer("Отлично, теперь вы можете настроить уведомления о просроченных заданиях(в разработке), "
                         "а также получать информацию об актуальных.", reply_markup=kb.uinb())
    await state.clear()


@router.callback_query(GetNS.day)
async def get_ns_day(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    start = await state.get_data()
    start = start['start']
    start = datetime.strptime(start, '%d.%m.%Y')
    if call.data in ["back_week", "next_week", "back"]:
        if call.data == "back":
            await state.clear()
            await call.message.answer("Вы вернулись в главное меню.", reply_markup=kb.uinb())
            await call.answer()
        else:
            if call.data == "back_week":
                start = start - timedelta(days=7)
            else:
                start = start + timedelta(days=7)
            end = start + timedelta(days=6)
            start = start.strftime('%d.%m.%Y')
            end = end.strftime('%d.%m.%Y')
            await call.message.answer(f"Выберете день на который вы хотите посмотреть\nТекущая неделя: {start} - {end}",
                                      reply_markup=kb.make_ns())
            await state.update_data(start=start)
            await call.answer()
    else:
        usersmessage = int(call.data)
        await state.update_data(day=usersmessage)
        l_p = get_student_by_telegram_id(call.from_user.id)
        try:
            await ns.login(l_p.login, l_p.password, 'Свято-Димитриевская школа')
            diary = await ns.diary(start=start)
            await ns.logout()
            await ns.logout()
            await ns.logout()
            day = diary.schedule[usersmessage]
        except SchoolNotFoundError or AuthError:
            await ns.logout()
            await state.clear()
            await call.message.answer("Неверный логин/пароль.")
            return
        lesson = day.lessons
        message_text = []
        for less in lesson:
            assig = less.assignments
            if assig:
                for i in assig:
                    if i.mark is None:
                        if i.is_duty is True:
                            message_text.append(
                                f"⚠️ДОЛГ!\n{html.bold(i.type)}({less.subject})\n{i.content}")
                        else:
                            message_text.append(f"{html.bold(i.type)}({less.subject})\n{i.content}")
                    else:
                        message_text.append(
                            f"{html.bold(i.type)}({less.subject})\n{i.content} -- {html.bold(i.mark)}")
            else:
                message_text.append(f"{html.bold(less.subject)}\nЗаданий нет.")
        msg = "\n\n".join(message_text)
        if len(msg) > 4096:
            for x in range(0, len(msg), 4096):
                await call.message.answer(msg[x:x + 4096], parse_mode='HTML', reply_markup=kb.get_startkeyboard())
        else:
            await call.message.answer(msg, parse_mode='HTML', reply_markup=kb.get_startkeyboard())
        await call.message.answer("В настройках вы можете подписаться на ежедневные напоминания о "
                                  "просроченных заданиях", reply_markup=kb.uinb())
        await state.clear()


@router.callback_query(EditHomework.lesson)
async def edit_homework_lesson(call: CallbackQuery, state: FSMContext):
    await state.update_data(lesson=call.data)
    await call.message.answer("Напишите ДЗ")
    await state.set_state(EditHomework.homework)


@router.message(EditHomework.homework)
async def edit_homework_text(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    usr = get_student_by_telegram_id(message.from_user.id)
    if get_homework(data['lesson'], usr.clas, data['day']) is not None:
        edit_homework(data['day'], data['lesson'], usr.clas, message.text)
        edit_homework_upd_date(data['day'], data['lesson'], usr.clas, str(datetime.now().strftime('%H:%M %d.%m.%Y')))
    else:
        create_homework(data['day'], data['lesson'], usr.clas, message.text,
                        str(datetime.now().strftime('%H:%M %d.%m.%Y')))
    await message.answer("Домашнее задание успешно добавлено.", reply_markup=kb.get_startkeyboard())
