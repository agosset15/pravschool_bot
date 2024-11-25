from aiogram import Router, F, Bot
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from tg_bot.models import DefaultService, Schedule, User
from tg_bot.keyboards.inline import inline_grades
from tg_bot.config import grades

router = Router()


@router.inline_query(F.query.in_(grades + ['10', '11']))
async def inline_clas(query: InlineQuery, db: DefaultService, bot: Bot):
    schedule = await db.get_one(Schedule, Schedule.grade.contains(query.query), Schedule.entity == 0)
    bot_username = (await bot.get_me()).username
    await query.answer(inline_grades(schedule, bot_username), cache_time=86400, is_personal=False,
                       switch_pm_text="Поговорить лично »»", switch_pm_parameter=f"{query.query}_inline")


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
    await query.answer(inline_grades(schedule, bot_username), cache_time=86400, is_personal=True,
                       switch_pm_text="Поговорить лично »»", switch_pm_parameter=f"{query.query}_inline")