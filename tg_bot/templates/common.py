from aiogram import html

from tg_bot.config import days
from tg_bot.models import User


def main(user: User):
    return ((f"Вы в учитель" if user.is_teacher else f"Вы в {user.grade} классе") +
            f".\nВыберете день, на который вы хотите увидеть расписание.\n"
            f"Вы можете выбрать расписание на неделю в ОСОБОМ МЕНЮ.\n"
            f"{html.link('Книга отзывов и предложений', 'tg://resolve?domain=agosset15bot')}")
