from aiogram import Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import Command, CommandStart

from tg_bot.filters.user import NewUserFilter
from tg_bot.models import DefaultService, User, Schedule
from tg_bot.templates import main_text
from tg_bot.config import LOG_CHAT, ADMIN_ID
from tg_bot.keyboards import main_kb, start_kb, admin_main_kb, settings_kb, inline_kb
from tg_bot.states.user import NSChild
from tg_bot.utils.ns import get_duty, NSError, NoResponseFromServer, get_ns_object
from tg_bot.utils.register import extract_unique_code, register

router = Router()


@router.message(NewUserFilter())
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, db: DefaultService, user: User, bot: Bot):
    await state.clear()
    code = extract_unique_code(message.text)
    grades = await db.get_all(Schedule, Schedule.entity == 0)
    grades_list = [x.grade for x in grades]
    if user is None:
        if code and code.split('_')[0] in grades_list:
            code_rs = code.split('_')
            await message.answer("""Вы всегда сможете изменить свой класс во вкладке "Настройки" в особом меню.""",
                                 reply_markup=start_kb())
            await db.create(User, chat_id=message.from_user.id, name=message.from_user.full_name,
                            username=message.from_user.username, grade=code_rs[0],
                            ref=(code_rs[1] if len(code_rs) > 1 else None))
            await message.answer(main_text(code_rs[0]), reply_markup=main_kb())
            print("Новый пользователь!")
            await bot.send_message(LOG_CHAT, f"{message.from_user.id} Новый пользователь!\n{code}")
        else:
            return await register(message, state, bot, db, code)
    else:
        if user.schedule is None:
            if user.grade in grades_list:
                grade = await db.get_one(Schedule, Schedule.entity == 0, Schedule.grade == user.grade)
                await db.update(User, User.id == user.id, schedule=grade.id)
            else:
                return await message.answer("Бот был обновлен. Выберите пожалуйста свой класс заново.",
                                            reply_markup=settings_kb())
        await message.answer("👨‍🏫", reply_markup=start_kb())
        if user.is_teacher is True:
            await message.answer(main_text(user), reply_markup=main_kb())
        else:
            await message.answer(main_text(user), reply_markup=main_kb())
    if message.from_user.id == ADMIN_ID:
        await message.answer("👑Ты в VIP-ке!", reply_markup=admin_main_kb())


@router.message(Command("stop"))
async def stop(state: FSMContext):
    await state.clear()


@router.message(Command("admin"))
async def cmd_admin(message: Message, user: User):
    if user.is_admin is True:
        await message.answer("Вы уже админ. Вы можете добавлять домашнее задание.")
    else:
        await message.answer("Вы не админ, но можете им стать, для этого напишите @ag15bots")


@router.message(Command('overdue'))
async def cmd_overdue(message: Message, state: FSMContext, user: User, bot: Bot):
    if user.is_ns is False:
        return await message.answer("У вас не введены данные ЭЖ. Для ввода нажмите на кнопку 'Данные для входа в ЭЖ':",
                                    reply_markup=settings_kb())
    try:
        ns = await get_ns_object(user)
        duty = await get_duty(bot, ns)
    except NoResponseFromServer as e:
        return await message.answer(' '.join(e.__notes__))
    except NSError as e:
        return await message.answer(' '.join(e.__notes__), reply_markup=settings_kb())
    if len(ns.students) > 1:
        await state.set_state(NSChild.duty)
        return await message.answer(f"Для ученика {ns.students[0]['nickName']}:\n"+duty+"\n\nВыберите ребенка:",
                                    reply_markup=inline_kb(
                                        **{str(i): child['nickName'] for i, child in enumerate(ns.students)}),
                                    disable_web_page_preview=True)
    await state.clear()
    return await message.answer(duty, disable_web_page_preview=True)
