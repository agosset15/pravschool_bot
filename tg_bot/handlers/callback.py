from datetime import datetime, timedelta
from aiogram import Router, F, html
from aiogram.types import CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext

from tg_bot.keyboards import (main_kb, settings_kb, inline_kb, remove_kb, days_kb, homework_lessons_kb, switch_inline_kb,
                              reply_kb)
from tg_bot.states.user import GradeWait, GetFreeRooms, RoomWait, NSLoginCredentialsWait
from tg_bot.models import DefaultService, User, Schedule, Lesson
from tg_bot.config import times, cache, ADMIN_ID

router = Router()


@router.callback_query(F.data == "year")
async def call_year(call: CallbackQuery):
    await cache.connect()
    photo_id = await cache.redis.get("pravschool_year_photo")
    await cache.disconnect()
    await call.message.edit_media(InputMediaPhoto(media=photo_id, caption="👆Расписание на год"), reply_markup=main_kb())
    await call.answer()


@router.callback_query(F.data == "settings")
async def call_settings(call: CallbackQuery):
    await call.message.edit_text("Настройки", reply_markup=settings_kb())
    await call.answer()


@router.callback_query(F.data == "change_class")
async def call_change_class(call: CallbackQuery, state: FSMContext, db: DefaultService):
    grades = await db.get_all(Schedule, Schedule.entity == 0)
    await call.message.answer("Выберете класс, в котором учитесь",
                              reply_markup=reply_kb(*[grade.grade for grade in grades],
                                                    placeholder="Выберите класс", adjust=7))
    await call.message.answer("Или нажмите на кнопку ниже, если вы учитель",
                              reply_markup=switch_inline_kb("Я учитель", "#teacher "))
    await state.set_state(GradeWait.grade)
    await call.answer()


@router.callback_query(F.data == "info")
async def call_info(call: CallbackQuery, db: DefaultService):
    count = await db.count(User, User.blocked == False)
    admin = await db.get_one(User, User.chat_id == ADMIN_ID)
    await call.message.answer(f"Всего пользователей: {count}\n"
                              f"Для связи с администратором: {admin.mention}\n"
                              f"Исходный код бота доступен на "
                              f"{html.link('GitHub', 'https://github.com/agosset15/pravschool_bot')}.",
                              reply_markup=settings_kb())
    await call.answer()


@router.callback_query(F.data == "back")
async def call_back(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("Вы вернулись в главное меню.", reply_markup=main_kb())
    await call.answer()


@router.callback_query(F.data == "delete_me")
async def call_delete(call: CallbackQuery, user: User, db: DefaultService):
    await db.delete(User, User.id == user.id)
    await call.message.answer(
        "Вы успешно удалены из базы данных бота.\nПожалуйста, нажмите /start для продолжения.",
        reply_markup=remove_kb())
    await call.answer()


@router.callback_query(F.data == 'week')
async def call_week(call: CallbackQuery, db: DefaultService, user: User):
    schedule = await db.get_one(Schedule, Schedule.id == user.schedule)
    message_text = []
    for day in schedule.days:
        message_text.append(html.bold(day.name + ':') + "\n" + day.text)
    await call.message.edit_text('\n\n'.join(message_text), reply_markup=main_kb())


@router.callback_query(F.data == "now")
async def call_now(call: CallbackQuery, user: User, db: DefaultService):
    weekday = datetime.now().weekday()
    if weekday > 4:
        return await call.answer('Сегодня выходной')
    day = (await db.get_one(Schedule, Schedule.id == user.schedule)).days[weekday]
    await call.message.answer(day.text)
    await call.answer()


@router.callback_query(F.data == "tom")
async def call_tom(call: CallbackQuery, db: DefaultService, user: User):
    weekday = (datetime.now() + timedelta(days=1)).weekday()
    if weekday > 4:
        return await call.answer('Завтра выходной')
    day = (await db.get_one(Schedule, Schedule.id == user.schedule)).days[weekday]
    await call.message.answer(day.text)
    await call.answer()


@router.callback_query(F.data == 'homework')
async def call_homework(call: CallbackQuery):
    await call.message.edit_text("Выберете день", reply_markup=days_kb(['mon', 'tue', 'wed', 'thu', 'fri']))


@router.callback_query(F.data.in_(['mon', 'tue', 'wed', 'thu', 'fri']))
async def call_homework_day(call: CallbackQuery, user: User, db: DefaultService):
    data = {'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3, 'fri': 4}
    weekday = data[call.data]
    text = f"Важно! Это ДЗ может быть устаревшим. Проверяйте дату добавления."
    if user.is_admin:
        text += "\n\nВы можете добавлять домашнее задание, нажав кнопку ниже"
    day = (await db.get_one(Schedule, Schedule.id == user.schedule)).days[weekday]
    await call.message.edit_text(text, reply_markup=homework_lessons_kb(day.lessons, weekday, user.is_admin))


@router.callback_query(F.data.startswith("hw_"))
async def call_get_hw_lesson(call: CallbackQuery, db: DefaultService):
    lesson_id = int(call.data.split('_')[1])
    lesson = await db.get_one(Lesson, Lesson.id == lesson_id, joined=Lesson.homework)
    text = f"{lesson.name} - Нет"
    if lesson.homework:
        text = (f"{html.bold(lesson.name)}\n\n{lesson.homework.homework} "
                f"(Добавлено <i>{lesson.homework.updated_at.strftime('%d-%m-%Y, %H:%M')}</i>)")
        if lesson.homework.image:
            return await call.message.edit_media(InputMediaPhoto(media=lesson.homework.image, caption=text),
                                                 reply_markup=inline_kb(back='Назад'))
    await call.message.answer(text, reply_markup=inline_kb(back='Назад'))


@router.callback_query(F.data == "kabs_free")
async def get_kabs_free(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("Выберите день:", reply_markup=days_kb(list(range(6)), extra_text='Суббота'))
    await state.set_state(GetFreeRooms.day)
    await call.answer()


@router.callback_query(F.data == "kab")
async def call_room(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("Введите номер кабинета из списка выше",
                                 reply_markup=inline_kb(switch_text="Найти кабинет", switch_param="#room",
                                                        kabs_free='Показать свободные'))
    await state.set_state(RoomWait.room)
    await call.answer()


@router.callback_query(F.data == "add_ns")
async def call_add_ns(call: CallbackQuery, state: FSMContext, user: User):
    if user.is_ns:
        return await call.message.edit_text("Вы уже ввели свои данные.\nВы можете ввести их заново, "
                                            "или подписаться на уведомления о просроченных заданиях.",
                                            reply_markup=inline_kb(change_ns="Изменить логин/пароль", back='Назад'))
    await call.message.edit_text("Пришлите свой логин(с учетом регистра)")
    await state.set_state(NSLoginCredentialsWait.login)
    await call.answer()


@router.callback_query(F.data == "change_ns")
async def call_change_ns(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("Пришлите свой логин(с учетом регистра)")
    await state.set_state(NSLoginCredentialsWait.login)


# @router.callback_query(F.data == "add_ns_upd")
# async def call_add_ns_ntf(call: CallbackQuery, user: User, db: DefaultService):
#     if user.duty_notification is False:
#         if user.is_ns is True:
#             await db.update(User, User.id == user.id, duty_notification=True)
#             await call.answer("Подключили вам уведомления. Они будут приходить каждый день в 12:00.",
#                               show_alert=True)
#         return await call.answer("У вас не введены данные для ЭЖ", show_alert=True)
#     return await call.answer("У вас уже подключены уведомления.")


@router.callback_query(F.data == "want_to_be_admin")
async def call_want_to_be_admin(call: CallbackQuery, db: DefaultService):
    admin = await db.get_one(User, User.chat_id == ADMIN_ID)
    await call.message.edit_text("Вы можете помочь развитию бота и своим одноклассникам или ученикам, "
                                 "добавляя домашние задания напрямую в бота, "
                                 "в случае затруднений в работе с электронным журналом.\n"
                                 f"Для этого надо получить специальное разрешение, написав: {admin.mention}",
                                 reply_markup=settings_kb())


@router.callback_query(F.data == "add_time")
async def add_time(call: CallbackQuery):
    # TODO: Исправить ошибку со временем в недельном просмотре
    await call.answer("Обновляю...")
    new = []
    day = call.message.text.split("\n")[0]
    for lesson, i in zip(call.message.text.split("\n")[1:], range(8)):
        n = f"{lesson.strip()} ({times[i]})"
        new.append(n)
    msg = html.bold(day) + "\n" + "\n".join(new)
    await call.message.edit_text(msg, reply_markup=inline_kb(del_time="Убрать время"))


@router.callback_query(F.data == "del_time")
async def del_time(call: CallbackQuery):
    await call.answer("Обновляю...")
    new = []
    day = call.message.text.split("\n")[0]
    for lesson, i in zip(call.message.text.split("\n")[1:], range(8)):
        if lesson.split('(')[1].strip()[:-1] in times:
            new.append(f"{lesson.split('(')[0]}")
        else:
            new.append(f"{lesson.split('(')[0]}({lesson.split('(')[1]}")
    msg = html.bold(day) + "\n" + "\n".join(new)
    await call.message.edit_text(msg, reply_markup=inline_kb(add_time="Посмотреть время"))
