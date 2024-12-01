from typing import List
import asyncio

from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError, TelegramNotFound

from tg_bot.states.admin import Advert, ExcelWait, PhotoAdd, EditHomework
from tg_bot.keyboards import reply_kb, main_kb, homework_lessons_kb
from tg_bot.models import DefaultService, User, Schedule, Homework
from tg_bot.config import ADMIN_ID, BOT_DIR, cache
from tg_bot.utils.add_rasp import ExcelParser

router = Router()
router.message.filter(F.from_user.id == ADMIN_ID)


@router.callback_query(F.data == "users_check")
async def clb_usr(call: CallbackQuery, db: DefaultService):
    users: List[User] = await db.get_all(User)
    message = "<b>Пользователи:</b>\n"
    for i in range(0, len(users), 120):
        await call.message.answer(message + '\n'.join([user.text for user in users[i:i + 120]]))
    await call.answer()


@router.callback_query(F.data == "ad")
async def call_ad(call: CallbackQuery, state: FSMContext):
    await call.message.answer('Введите текст объявления.')
    await state.set_state(Advert.text)
    await call.answer()


@router.message(Advert.text)
async def advert_text(message: Message, state: FSMContext, db: DefaultService, bot: Bot):
    await state.clear()
    users: List[User] = await db.get_all(User, User.blocked == False)
    for user in users:
        try:
            await bot.send_message(user.chat_id, message.text)
            await asyncio.sleep(0.2)
        except (TelegramBadRequest, TelegramForbiddenError, TelegramNotFound):
            await db.update(User, User.id == user.id, blocked=True)
            continue
    await message.answer("Готово!")


@router.message(Command("add_admin"))
async def admin_pswd_set(message: Message, db: DefaultService):
    await db.update(User, User.chat_id == int(message.text.strip('/add_admin ')), isAdmin=True)
    await message.answer("Done!")


@router.callback_query(F.data == "new_rasp")
async def call_new_rasp(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer("Пришлите пожалуйста файл с расширением .xlsx")
    await state.set_state(ExcelWait.file)


@router.message(F.document, ExcelWait.file)
async def admin_file(message: Message, state: FSMContext, db: DefaultService, bot: Bot):
    if not message.document:
        return await message.answer("Это не распознано как документ, повторите попытку.")
    destination = f"{BOT_DIR}/xl_uploads/{message.document.file_id}.xlsx"
    await db.delete(Schedule)
    await bot.download(file=message.document, destination=destination)
    await state.update_data(destination=destination)
    await message.answer("Давайте разберемся с расписаниями."
                         "\nНапишите количество классов, наименьший индекс строки и столбца с классным расписанием в "
                         "формате: количество число1 число2")
    await state.set_state(ExcelWait.students)


@router.message(ExcelWait.students)
async def admin_rasp(message: Message, state: FSMContext, db: DefaultService):
    userdata = message.text.split()
    data = await state.get_data()
    parser = ExcelParser(data['destination'], db)
    await parser.students(*[int(data) for data in userdata])
    await message.answer("Напишите количество учителей, наименьший индекс строки и столбца с учительским расписанием "
                         "в формате: количество число1 число2")
    await state.set_state(ExcelWait.teachers)


@router.message(ExcelWait.teachers)
async def admin_rasp(message: Message, state: FSMContext, db: DefaultService):
    userdata = message.text.split()
    data = await state.get_data()
    parser = ExcelParser(data['destination'], db)
    await parser.teachers(*[int(data) for data in userdata])
    await message.answer("Напишите количество кабинетов, наименьший индекс строки и столбца с расписанием по кабинетам "
                         "в формате: количество число1 число2")
    await state.set_state(ExcelWait.rooms)


@router.message(ExcelWait.rooms)
async def admin_kab(message: Message, state: FSMContext, db: DefaultService):
    userdata = message.text.split()
    data = await state.get_data()
    parser = ExcelParser(data['destination'], db)
    await parser.rooms(*[int(data) for data in userdata])
    await message.answer("Готово!\nПодождите минутку,и новое расписание добавится в бота.")
    await state.clear()


@router.callback_query(F.data == "photo_add")
async def call_photo_add(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Пришлите фото year")
    await state.set_state(PhotoAdd.year)


@router.message(F.photo, PhotoAdd.year)
async def photoadd_year(message: Message, state: FSMContext):
    await cache.redis.set("pravschool_year_photo", message.photo[-1].file_id)
    await message.answer("Получилось!")
    await state.clear()


@router.message(Command("del_user"))
async def del_user(message: Message, db: DefaultService):
    await db.delete(User, User.chat_id == int(message.text))
    await message.answer("Пользователь удален!")


@router.callback_query(F.data.endswith('_edit_homework'))
async def call_edit_homework(call: CallbackQuery, state: FSMContext, user: User, db: DefaultService):
    weekday = int(call.data.split('_')[0])
    day = (await db.get_one(Schedule, Schedule.id == user.schedule)).days[weekday]
    await call.message.edit_text("Выберете предмет", reply_markup=homework_lessons_kb(day.lessons, weekday,
                                                                                      user.is_admin, edit=True))
    await state.set_state(EditHomework.lesson)
    await state.update_data(day=day)
    await call.answer()


@router.callback_query(EditHomework.lesson)
async def edit_homework_lesson(call: CallbackQuery, state: FSMContext):
    await state.update_data(lesson=call.data)
    await call.message.answer("Отправьте текст задания",
                                 reply_markup=reply_kb("Не добавлять", placeholder="Отправьте домашнее задание"))
    await state.set_state(EditHomework.homework)


@router.message(EditHomework.homework)
async def edit_homework_text(message: Message, state: FSMContext):
    text = message.text
    if message.text == "Не добавлять":
        text = "   "
    await state.update_data(homework=text)
    await message.answer("Отправьте изображение",
                         reply_markup=reply_kb("Не добавлять", placeholder="Отправьте изображение"))
    await state.set_state(EditHomework.image)


@router.message(EditHomework.image)
async def edit_homework_image(message: Message, state: FSMContext, db: DefaultService):
    image = None
    if message.text != "Не добавлять":
        image = message.photo[-1].file_id
    data = await state.get_data()
    await state.clear()
    homework = await db.get_one(Homework, Homework.lesson_id == data['lesson'])
    if homework:
        await db.update(Homework, Homework.id == homework.id, homework=data['homework'], image=image)
    else:
        await db.create(Homework, lesson_id=data['lesson'], homework=data['homework'], image=image)
    await message.answer("Домашнее задание успешно добавлено.", reply_markup=main_kb())
