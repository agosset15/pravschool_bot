from aiogram import html
from aiogram.types import InlineQueryResultArticle, InputTextMessageContent
from aiogram.utils.link import create_telegram_link

from tg_bot.keyboards import url_kb
from tg_bot.models import Schedule


def inline_grades(schedule: Schedule, bot_username):
    kb = url_kb(**{create_telegram_link(bot_username, start='inline_button'): 'Все расписание'})
    week = []
    buttons = []
    thumbnail_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
    for i, day in enumerate(schedule.days):
        buttons.append(InlineQueryResultArticle(id=f"{day.name}_{schedule.grade}", title=day.name,
                                                input_message_content=InputTextMessageContent(
                                                    message_text=f"{schedule.grade}: <b>{day.name}</b>:\n{day.text}",
                                                    parse_mode='HTML'),
                                                reply_markup=kb,
                                                thumbnail_url=f"https://static.ag15.ru/pravschool/{thumbnail_names[i]}.png",
                                                thumbnail_width=512, thumbnail_height=512))
        week.append(html.bold(day.name + ':') + "\n" + day.text)
    buttons.append(InlineQueryResultArticle(id=f"week_{schedule.grade}", title="На неделю",
                                            input_message_content=InputTextMessageContent(
                                                message_text=f"{schedule.grade}: "+'\n\n'.join(week),
                                                parse_mode='HTML'),
                                            reply_markup=kb,
                                            thumbnail_url="https://static.ag15.ru/pravschool/week.png",
                                            thumbnail_height=512,
                                            thumbnail_width=512))
    return buttons


def inline_schedule(schedules: list[Schedule], prefix: str = 'schedule'):
    buttons = []
    for schedule in schedules:
        buttons.append(InlineQueryResultArticle(id=f"{prefix}_{schedule.id}", title=schedule.grade,
                                                input_message_content=InputTextMessageContent(
                                                    message_text=f"*{prefix}_{schedule.id}")))
    return buttons
