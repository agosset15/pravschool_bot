import time
import ast
from datetime import datetime, timedelta
from aiogram import Router, html
from aiogram.filters import Text
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from db.methods.get import get_count, get_student_by_telegram_id, get_schedule, get_teacher_schedule, get_homework
from db.methods.delete import delete_student
from db.methods.update import switch_student_duty_notification
from ..keyboards import keyboards as kb
from ..config import *

router = Router()

sp = ["year", "settings", "change_class", "info", "back", "delete", "del_user", "ns", 'week']
admin_id = 900645059


@router.callback_query(Text(sp))
async def special(call: CallbackQuery, state: FSMContext):
    if call.data == "year":
        await call.message.delete()
        with open("ids.txt", "r", encoding='utf-8') as text_id:
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
        value = get_count()
        await call.message.answer(f"Всего пользователей: {value}\nНовых отзывов и предложений нет.",
                                  reply_markup=kb.settings())
        await call.answer()
    if call.data == "back":
        await state.clear()
        await call.message.delete()
        await call.message.answer("Вы вернулись в главное меню.", reply_markup=kb.uinb())
        await call.answer()
    if call.data == "delete":
        delete_student(call.from_user.id)
        await call.message.answer(
            "Вы успешно удалены из базы данных бота.\nПожалуйста, нажмите /start для продолжения.",
            reply_markup=kb.rem())
        await call.answer()
    if call.data == "del_user":
        await call.message.answer("Введите id пользователя")
        await state.set_state(DelUser.id)
    if call.data == "ns":
        if get_student_by_telegram_id(call.from_user.id).isNs == 1:
            dt = datetime.now()
            start = dt - timedelta(days=dt.weekday())
            end = start + timedelta(days=6)
            start = start.strftime('%d.%m.%Y')
            end = end.strftime('%d.%m.%Y')
            await call.message.answer(f"Выберете день на который вы хотите посмотреть\nТекущая неделя: {start} - {end}",
                                      reply_markup=kb.make_ns())
            await state.set_state(GetNS.day)
            await state.update_data(start=start)
        else:
            await call.message.answer("Вы не ввели свои данные. Введите их в меню настроек.")
            await call.message.answer(f"Внимание!!!\n\nДанная функция пока доступна ТОЛЬКО для {html.bold('личных')}"
                                      f"(не родительских и не учительских) дневников ОО АНО СОШ Димитриевская!"
                                      f"(не заочное отделение и не началка на Якиманке)", parse_mode='HTML')
        await call.answer()
    if call.data == 'week':
        usr = get_student_by_telegram_id(call.from_user.id)
        clas = usr.clas
        try:
            if usr.isTeacher == 0:
                value = []
                for i in range(1, 6):
                    value.append('\n'.join(ast.literal_eval(get_schedule(clas, i))))
                await call.message.answer(f"<b>Понедельник:</b>\n{value[0]}\n\n<b>Вторник:</b>\n{value[1]}"
                                          f"\n\n<b>Среда:</b>\n{value[2]}\n\n<b>Четверг:</b>\n{value[3]}"
                                          f"\n\n<b>Пятница:</b>\n{value[4]}",
                                          reply_markup=kb.get_startkeyboard(), parse_mode='HTML')
                await call.answer()
            elif usr.isTeacher == 1:
                value = []
                for i in range(1, 6):
                    value.append('\n'.join(ast.literal_eval(get_teacher_schedule(clas, i))))
                await call.message.answer(f"<b>Понедельник:</b>\n{value[0]}\n\n<b>Вторник:</b>\n{value[1]}"
                                          f"\n\n<b>Среда:</b>\n{value[2]}\n\n<b>Четверг:</b>\n{value[3]}"
                                          f"\n\n<b>Пятница:</b>\n{value[4]}",
                                          reply_markup=kb.get_startkeyboard(), parse_mode='HTML')
                await call.answer()
            else:
                await call.message.answer("Ошибка!\nНажмите пожалуйста /start")
                await call.answer()
        except TypeError or ValueError:
            await call.message.answer("Извините, сейчас расписание обновляется. Попробуйте еще раз через минутку.")
            await bot.send_message(admin_id, f"{call.from_user.id} - ошибка колл\учителей(учеников)")
            print(call.from_user.id)
            await bot.send_message(-1001845347264, f"{call.from_user.id} ошибка колл\учителей(учеников)")


@router.callback_query(Text("now"))
async def call_now(call: CallbackQuery):
    try:
        usr = get_student_by_telegram_id(call.from_user.id)
        clas = usr.clas
        if usr.isTeacher == 0:
            day = time.localtime()
            day = day.tm_wday + 1
            if day < 6:
                value = get_schedule(clas, day)
                value = '\n'.join(ast.literal_eval(value))
                await call.message.answer(f"{value}")
            else:
                await call.message.answer("Сегодня выходной!")
            await call.answer()
        else:
            day = time.localtime()
            day = day.tm_wday + 1
            if day < 6:
                value = get_teacher_schedule(clas, day)
                value = '\n'.join(ast.literal_eval(value))
                await call.message.answer(f"{value}")
            else:
                await call.message.answer("Сегодня выходной!")
            await call.answer()
    except TypeError or ValueError:
        await call.message.answer("Извините, сейчас расписание обновляется. Попробуйте еще раз через минутку.")
        await bot.send_message(admin_id, f"{call.from_user.id} - ошибка колл\сегодня")
        print(call.from_user.id)
        await bot.send_message(-1001845347264, f"{call.from_user.id}ошибка колл\сегодня")


@router.callback_query(Text("tom"))
async def call_tom(call: CallbackQuery):
    try:
        usr = get_student_by_telegram_id(call.from_user.id)
        clas = usr.clas
        if usr.isTeacher == 0:
            day = time.localtime()
            day = day.tm_wday + 2
            userbase = [6, 7]
            if day < 6:
                value = get_schedule(clas, day)
                value = '\n'.join(ast.literal_eval(value))
                await call.message.answer(f"{value}")
            elif day == 8:
                value = get_schedule(clas, day)
                await call.message.answer(f"{value}")
            elif day in userbase:
                await call.message.answer("Завтра выходной!")
            await call.answer()
        else:
            day = time.localtime()
            day = day.tm_wday + 2
            userbase = [6, 7]
            if day < 6 or day == 8:
                value = get_teacher_schedule(clas, day)
                value = '\n'.join(ast.literal_eval(value))
                await call.message.answer(f"{value}")
            elif day in userbase:
                await call.message.answer("Завтра выходной!")
            await call.answer()
    except TypeError or ValueError:
        await call.message.answer("Извините, сейчас расписание обновляется. Попробуйте еще раз через минутку.")
        await bot.send_message(admin_id, f"{call.from_user.id} - ошибка колл\завтра")
        print(call.from_user.id)
        await bot.send_message(-1001845347264, f"{call.from_user.id} ошибка колл\завтра")


@router.callback_query(Text('homework'))
async def call_homework(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer("Выберете день", reply_markup=kb.days_inline())
    await call.answer()


@router.callback_query(Text(['mon', 'tue', 'wed', 'thu', 'fri']))
async def call_homework_day(call: CallbackQuery):
    await call.message.delete()
    usr = get_student_by_telegram_id(call.from_user.id)
    data = {'mon': 1, 'tue': 2, 'wed': 3, 'thu': 4, 'fri': 5}
    wday = data[call.data]
    day = ast.literal_eval(get_schedule(usr.clas, wday))
    homework = []
    for i in range(1, len(day) + 1):
        hm = get_homework(i, usr.clas, wday)
        if hm is None:
            homework.append(f"{day[i - 1]} - Нет")
        else:
            homework.append(f"{day[i - 1]} - {hm.homework}(Добавлено {hm.upd_date})")
    text = '\n'.join(homework)
    if usr.isAdmin == 1:
        await call.message.answer(f"Важно! Это ДЗ может быть устаревшим. Проверяйте дату добавления."
                                  f"\n\n{text}\n\nВы можете добавлять домашнее задание, нажав кнопку ниже",
                                  reply_markup=kb.admin_kb(wday))
    else:
        await call.message.answer(f"Важно! Это ДЗ может быть устаревшим. Проверяйте дату добавления."
                                  f"\n\n{text}", reply_markup=kb.back())
    await call.answer()


@router.callback_query(Text(endswith='edit_homework'))
async def call_edit_homework(call: CallbackQuery, state: FSMContext):
    day = call.data.split('_')[0]
    usr = get_student_by_telegram_id(call.from_user.id)
    day_rasp = ast.literal_eval(get_schedule(usr.clas, int(day)))
    await call.message.answer("Выберете предмет", reply_markup=kb.rasp_kb(day_rasp))
    await state.set_state(EditHomework.lesson)
    await state.update_data(day=day)
    await call.answer()


@router.callback_query(
    Text(["new_rasp", "admin_add", "edit", "ad", "uch", "kab", "photo_add", "add_ns", "change_ns", "add_ns_upd",
          "wanttobeadmin"]))
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
        with open("ids.txt", "r", encoding='utf-8') as text_id:
            photo_id = text_id.read()
        photo_id = photo_id.strip("[]").split(',')[1].strip(" ''")
        await call.message.answer_photo(photo_id, caption="Введите свой номер из списка выше",
                                        reply_markup=kb.rem())
        await state.set_state(ClassWait.uch)
        await call.answer()
    if call.data == "kab":
        with open("ids.txt", "r", encoding='utf-8') as text_id:
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
    if call.data == "add_ns":
        if get_student_by_telegram_id(call.from_user.id).isNs == 0:
            await call.message.answer(f"Внимание!!!\n\nДанная функция пока доступна ТОЛЬКО для {html.bold('личных')}"
                                      f"(не родительских и не учительских) дневников ОО АНО СОШ Димитриевская!"
                                      f"(не заочное отделение и не началка на Якиманке)", parse_mode='HTML')
            await call.message.answer("Пришлите свой логин(с учетом регистра)")
            await state.set_state(AddNS.login)
            await call.answer()
        else:
            await call.message.answer("Вы уже ввели свои данные.\nВы можете ввести их заново, или подписаться на "
                                      "уведомления о просроченных заданиях.",
                                      reply_markup=kb.ns_settings())
            await call.answer()
        await call.answer()
    if call.data == "change_ns":
        await call.message.answer("Пришлите свой логин(с учетом регистра)")
        await state.set_state(AddNS.login)
        await call.answer()
    if call.data == "add_ns_upd":
        usr = get_student_by_telegram_id(call.from_user.id)
        if usr.duty_notification is False:
            if usr.isNs is True:
                switch_student_duty_notification(call.from_user.id)
                await call.message.answer("Подключили вам уведомления. Они будут приходить каждый день в 12:00.")
                await call.answer()
            else:
                await call.answer("У вас не введены данные для ЭЖ", show_alert=True)
        elif usr.duty_notification is True:
            await call.answer("У вас уже подключены уведомления.")
    if call.data == "wanttobeadmin":
        await call.message.answer("Вы можете добавлять домашнее задание для своего класса прямо в боте."
                                  "\nДля того, чтобы получить  такую возможность, нужно написать администратору "
                                  "@ag15bots", reply_markup=kb.settings())
        await call.answer()
