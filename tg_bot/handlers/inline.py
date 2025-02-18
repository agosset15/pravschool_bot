from aiogram import Router, F, Bot
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from tg_bot.models import DefaultService, Schedule, User
from tg_bot.keyboards.inline import inline_grades, inline_schedule
from tg_bot.config import grades, ADMIN_ID
from tg_bot.states import RoomWait, GradeWait

router = Router()


@router.inline_query(F.query.in_(grades + ['10', '11']))
async def inline_clas(query: InlineQuery, db: DefaultService, bot: Bot):
    await bot.send_message(ADMIN_ID, f"inline reached: {query.query}")
    schedule = await db.get_one(Schedule, Schedule.grade.contains(query.query), Schedule.entity == 0)
    bot_username = (await bot.get_me()).username
    await query.answer(inline_grades(schedule, bot_username), cache_time=0, is_personal=False,
                       switch_pm_text=f"{schedule.grade}  Поговорить лично »»", switch_pm_parameter=f"{query.query}_inline")


@router.inline_query(GradeWait.grade, F.query.startswith("#teacher"))
async def grade_teacher(query: InlineQuery, db: DefaultService):
    name = query.query[9:]
    teachers = await db.get_all(Schedule, Schedule.entity == 1, Schedule.grade.icontains(name))
    await query.answer(inline_schedule(teachers, 'teacher'), is_personal=False, cache_time=0)


@router.inline_query(RoomWait.room, F.query.contains("#room"))
async def room_find(query: InlineQuery, db: DefaultService):
    room = query.query[6:]
    rooms = await db.get_all(Schedule, Schedule.entity == 2, Schedule.grade.icontains(room))
    await query.answer(inline_schedule(rooms, 'room'), cache_time=0)


@router.inline_query()
async def inline_day(query: InlineQuery, user: User, db: DefaultService, bot: Bot):
    if user is None or user.grade == 0:
        buttons = [
            InlineQueryResultArticle(id="err", title="Вы не зарегистрированы!",
                                     description="Зарегистрируйтесь по кнопке выше, или напишите класс",
                                     input_message_content=InputTextMessageContent(message_text='Ошибка!'))]
        return await query.answer(buttons, cache_time=1, is_personal=True, switch_pm_parameter="inline",
                                  switch_pm_text="Регистрация »»")
    schedule = await db.get_one(Schedule, Schedule.id == user.schedule, Schedule.entity == 0)
    bot_username = (await bot.get_me()).username
    await query.answer(inline_grades(schedule, bot_username), cache_time=0, is_personal=True,
                       switch_pm_text="Поговорить лично »»", switch_pm_parameter=f"{query.query}_inline")
