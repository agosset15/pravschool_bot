import datetime
import time
import ast
from aiogram import Router, F, html
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError, TelegramNotFound
from netschoolapi.errors import SchoolNotFoundError, AuthError, NoResponseFromServer

from ..backend.add_rasp import Exel
from db.methods.update import (edit_student_clas, switch_student_admin, edit_student_login, edit_student_password,
                               edit_homework, edit_homework_upd_date, switch_student_ns, switch_student_teasher_false,
                               switch_student_teasher_true, update_student_blocked, switch_student_parent)
from db.methods.create import create_homework
from db.methods.get import get_kab_schedule, get_all_students, get_student_by_telegram_id, get_homework
from db.methods.delete import delete_schedules, delete_student
from ..keyboards import keyboards as kb
from ..backend.notifications import get_duty
from ..config import *

router = Router()

days = ["📕ПОНЕДЕЛЬНИК📕", "📗ВТОРНИК📗", "📘СРЕДА📘", "📙ЧЕТВЕРГ📙", "📔ПЯТНИЦА📔"]


@router.message(ClassWait.clas)
async def classadd(message: Message, state: FSMContext):
    class_list = ["10г", "10е", "10ф", "11г", "11е", "11ф"]
    list1 = {'10г': '101', "10е": "102", '10ф': '103', '11г': '111', '11е': '112', '11ф': '113'}
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
    await message.answer("Выберите день, на который вы хотите увидеть расписание\."
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
                         f"\n\n<b>Пятница:</b>\n{value[4]}", reply_markup=kb.inline_text_kb("Посмотреть время", 'add_time'), parse_mode='HTML')
    await state.clear()


@router.message(Admad.ad)
async def getcount(message: Message, state: FSMContext):
    ad = message.text
    await state.update_data(ad=ad)
    await state.clear()
    userbase = get_all_students()
    for z in userbase:
        try:
            await bot.send_message(z.tgid, f"{ad}", parse_mode="HTML")
        except TelegramBadRequest or TelegramForbiddenError or TelegramNotFound:
            update_student_blocked(z.tgid)
            pass
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
    await message.answer(f"Теперь пришлите свой пароль."
                         f"\nВсе пароли хранятся в боте в {html.underline('зашифрованном виде')} и никуда не передаются.",
                         parse_mode='HTML')
    await state.set_state(AddNS.password)


@router.message(AddNS.password)
async def add_ns_login(message: Message, state: FSMContext):
    data = await state.get_data()
    try:
        p = await ns.login(data['login'], message.text, 1)
    except AuthError:
        await message.answer("Неверные данные. Попробуйте еще раз.", reply_markup=kb.settings())
        await state.clear()
        return
    edit_student_login(message.from_user.id, data['login'])
    edit_student_password(message.from_user.id, f"{p}")
    switch_student_ns(message.from_user.id)
    st = await ns.students()
    if len(st[0]) > 1:
        switch_student_parent(message.from_user.id)
    await message.answer("Отлично, теперь вы можете настроить уведомления о просроченных заданиях(в разработке), "
                         "а также получать информацию об актуальных.", reply_markup=kb.uinb())
    await state.clear()
    await ns.logout()
    await ns.logout()
    await ns.logout()


@router.callback_query(GetNS.day)
async def get_ns_day(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    start = await state.get_data()
    start = start['start']
    start = datetime.strptime(start, '%d.%m.%Y')
    if call.data == 'homework':
        await state.clear()
        await call.message.answer("Выберете день", reply_markup=kb.days_inline())
    elif call.data in ["back_week", "next_week", "back"]:
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
        d = datetime.date(start + timedelta(days=usersmessage))
        try:
            await ns.login(l_p.login, l_p.password, 1)
            stt = await ns.students()
            diary = await ns.diary(start=start)
            await ns.logout()
            await ns.logout()
            await ns.logout()
            day = next((item for item in diary.schedule if item.day == d), None)
        except AuthError:
            await ns.logout()
            await state.clear()
            await call.message.answer("Неверный логин/пароль.")
            return
        except NoResponseFromServer:
            await call.message.answer("Нет ответа от сервера. Повторите попытку.",
                                      reply_markup=kb.inline_text_kb("Повторить попытку", call.data))
            return
        if l_p.isParent is True:
            st = []
            for i in stt[0]:
                st.append(i['nickName'])
            await call.message.answer("Выберите ребенка:", reply_markup=kb.arr_kb(st))
            await state.set_state(GetNS.child)
            return
        lesson = day.lessons
        message_text = []
        for less in lesson:
            assig = less.assignments
            if assig:
                for i in assig:
                    link = f"t.me/pravschool_bot/journal?startapp={d.strftime('%Ya%ma%d')}a{less.lesson_id}a{i.id}"
                    if i.mark is None:
                        if i.is_duty is True:
                            message_text.append(
                                f"⚠️ДОЛГ!\n{html.bold(i.type)}({less.subject}) {html.link('·?·', link)}\n{i.content}")
                        else:
                            message_text.append(
                                f"{html.bold(i.type)}({less.subject}) {html.link('·?·', link)}\n{i.content}")
                    else:
                        message_text.append(
                            f"{html.bold(i.type)}({less.subject}) {html.link('·?·', link)}\n{i.content} -- {html.bold(i.mark)}")
            else:
                message_text.append(f"{html.bold(less.subject)}\nЗаданий нет.")
        msg = "\n\n".join(message_text)
        if len(msg) > 4096:
            for x in range(0, len(msg), 4096):
                await call.message.answer(msg[x:x + 4096], parse_mode='HTML', reply_markup=kb.get_startkeyboard(),
                                          disable_web_page_preview=True)
        else:
            await call.message.answer(msg, parse_mode='HTML', reply_markup=kb.get_startkeyboard(),
                                      disable_web_page_preview=True)
        await call.message.answer("В настройках вы можете подписаться на ежедневные напоминания о "
                                  "просроченных заданиях", reply_markup=kb.uinb())
        await state.clear()


@router.callback_query(GetNS.child)
async def get_ns_child(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await state.update_data(child=call.data)
    data = await state.get_data()
    start = data['start']
    start = datetime.strptime(start, '%d.%m.%Y')
    usersmessage = int(data['day'])
    l_p = get_student_by_telegram_id(call.from_user.id)
    d = datetime.date(start + timedelta(days=usersmessage))
    try:
        await ns.login(l_p.login, l_p.password, 1)
        stt = await ns.students()
        child_id = stt[0][int(call.data)]['studentId']
        diary = await ns.diary(start=start, student_id=child_id)
        await ns.logout()
        await ns.logout()
        await ns.logout()
        day = next((item for item in diary.schedule if item.day == d), None)
    except SchoolNotFoundError or AuthError:
        await ns.logout()
        await state.clear()
        await call.message.answer("Неверный логин/пароль.")
        return
    except NoResponseFromServer:
        await call.message.answer("Нет ответа от сервера. Повторите попытку.",
                                  reply_markup=kb.inline_text_kb("Повторить попытку", call.data))
        return
    lesson = day.lessons
    message_text = []
    for less in lesson:
        assig = less.assignments
        if assig:
            for i in assig:
                link = f"t.me/pravschool_bot/journal?startapp={d.strftime('%Ya%ma%d')}a{less.lesson_id}a{i.id}a{child_id}"
                if i.mark is None:
                    if i.is_duty is True:
                        message_text.append(
                            f"⚠️ДОЛГ!\n{html.bold(i.type)}({less.subject}) {html.link('·?·', link)}\n{i.content}")
                    else:
                        message_text.append(
                            f"{html.bold(i.type)}({less.subject}) {html.link('·?·', link)}\n{i.content}")
                else:
                    message_text.append(
                        f"{html.bold(i.type)}({less.subject}) {html.link('·?·', link)}\n{i.content} -- {html.bold(i.mark)}")
        else:
            message_text.append(f"{html.bold(less.subject)}\nЗаданий нет.")
    msg = "\n\n".join(message_text)
    if len(msg) > 4096:
        for x in range(0, len(msg), 4096):
            await call.message.answer(msg[x:x + 4096], parse_mode='HTML', reply_markup=kb.get_startkeyboard(),
                                      disable_web_page_preview=True)
    else:
        await call.message.answer(msg, parse_mode='HTML', reply_markup=kb.get_startkeyboard(),
                                  disable_web_page_preview=True)
    await call.message.answer("В настройках вы можете подписаться на ежедневные напоминания о "
                              "просроченных заданиях", reply_markup=kb.uinb())
    await state.clear()


@router.callback_query(GetDuty.child)
async def get_duty_child(call: CallbackQuery, state: FSMContext):
    child = int(call.data)
    await call.answer("Загрузка долгов...")
    user = get_student_by_telegram_id(call.from_user.id)
    try:
        await ns.login(user.login, user.password, 1)
        stt = await ns.students()
        chid = stt[0][child]['studentId']
        await ns.logout()
        await ns.logout()
        await ns.logout()
    except SchoolNotFoundError or AuthError:
        await ns.logout()
        await state.clear()
        await call.message.answer("Неверный логин/пароль.")
        return
    except NoResponseFromServer:
        await call.message.answer("Нет ответа от сервера. Повторите попытку.",
                                  reply_markup=kb.inline_text_kb("Повторить попытку", call.data))
        return
    duty = await get_duty(user, chid)
    if duty:
        await call.message.answer(duty, parse_mode="HTML", disable_web_page_preview=True)
    else:
        await call.message.answer("Ошибка!")
    await state.clear()


@router.callback_query(EditHomework.lesson)
async def edit_homework_lesson(call: CallbackQuery, state: FSMContext):
    await state.update_data(lesson=call.data)
    await call.message.answer("Отправьте текст задания",
                              reply_markup=kb.reply_text_kb("Не добавлять", "Отправьте домашнее задание"))
    await state.set_state(EditHomework.homework)


@router.message(EditHomework.homework)
async def edit_homework_text(message: Message, state: FSMContext):
    text = message.text
    if message.text == "Не добавлять":
        text = "   "
    await state.update_data(homework=text)
    await message.answer("Отправьте изображение",
                         reply_markup=kb.reply_text_kb("Не добавлять", "Отправьте изображение"))
    await state.set_state(EditHomework.image)


@router.message(EditHomework.image)
async def edit_homework_image(message: Message, state: FSMContext):
    if message.text != "Не добавлять":
        image = message.photo[-1].file_id
    else:
        image = None
    data = await state.get_data()
    await state.clear()
    usr = get_student_by_telegram_id(message.from_user.id)
    if get_homework(data['lesson'], usr.clas, data['day']) is not None:
        edit_homework(data['day'], data['lesson'], usr.clas, data['homework'], image)
        edit_homework_upd_date(data['day'], data['lesson'], usr.clas, str(datetime.now().strftime('%H:%M %d.%m.%Y')))
    else:
        create_homework(data['day'], data['lesson'], usr.clas, data['homework'],
                        str(datetime.now().strftime('%H:%M %d.%m.%Y')), image)
    await message.answer("Домашнее задание успешно добавлено.", reply_markup=kb.get_startkeyboard())


@router.message(GetFreeKabs.day)
async def day_kabs_free(message: Message, state: FSMContext):
    await state.clear()
    dase = {'ПОНЕДЕЛЬНИК': 1, 'ВТОРНИК': 2, 'СРЕДА': 3,
            'ЧЕТВЕРГ': 4, 'ПЯТНИЦА': 5}
    day = dase[message.text] if message.text != "СЕГОДНЯ" else None
    if day is None:
        day = time.localtime()
        day = day.tm_wday + 1
    if day < 6:
        result = []
        kabs = {1: "103", 2: "104", 3: "105", 4: "107", 5: "123", 6: "127", 7: "132", 8: "133",
                9: "135", 10: "110а", 11: "110б", 12: "122", 13: "240", 14: "239", 15: "242", 16: "306", 17: "Ул",
                18: "130", 19: "105б", 20: "115", 21: "116", 22: "201", 23: "204", 24: "Храм"}
        times = ['08:40 - 09:25', '09:35 - 10:20', '10:30 - 11:15', '11:25 - 12:10', '12:25 - 13:10', '13:25 - 14:10',
                 '14:25 - 15:10', '15:25 - 16:10']
        for lesson in range(1, 9):
            les = []
            for kab in range(1, 23):
                value: list[str] = ast.literal_eval(get_kab_schedule(kab, day))
                if value[lesson - 1][2:] == ' ':
                    les.append(kabs[kab])
            a = '\n   '.join(les)
            result.append(f"{html.bold(lesson)}({times[lesson-1]}):\n   {a}")
        res = '\n\n'.join(result)
        await message.answer(f"{message.text}, свободные кабинеты:\n\n{res}", reply_markup=kb.get_startkeyboard(),
                             parse_mode='HTML')
    else:
        await message.answer("Сегодня выходной!", reply_markup=kb.get_startkeyboard())
