from typing import List
from aiogram.types import SwitchInlineQueryChosenChat, WebAppInfo, ReplyKeyboardMarkup, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from tg_bot.config import grades as grades_list
from tg_bot.config import days as days_list
from tg_bot.models import Lesson


def main():
    kb = InlineKeyboardBuilder()
    kb.button(text="Сегодня", callback_data="now")
    kb.button(text="Завтра", callback_data="tom")
    kb.button(text="Кабинеты", callback_data="kab")

    kb.button(text="Неделя", callback_data="week"),
    kb.button(text="Год", callback_data="year"),
    kb.button(text="ДЗ", callback_data="ns"),
    kb.button(text="Настройки", callback_data="settings")

    kb.button(text="Режим 'в строке'",
              switch_inline_query_chosen_chat=SwitchInlineQueryChosenChat(allow_bot_chats=False,
                                                                          allow_user_chats=True,
                                                                          allow_channel_chats=True,
                                                                          allow_group_chats=True))
#    kb.button(text="Веб-приложение", web_app=WebAppInfo(url='https://tg.ag15.ru/rasp'))
    kb.adjust(3, 4, 2)
    return kb.as_markup()


def start(extra_text: str = None) -> ReplyKeyboardMarkup:
    buttons = days_list + ["Меню"]
    if extra_text:
        buttons[-1] = extra_text
    kb = ReplyKeyboardBuilder()
    for i in buttons:
        kb.button(text=i)
    kb.adjust(3)
    return kb.as_markup(resize_keyboard=True, input_field_placeholder="Нажмите на кнопку ниже")


def grades():
    kb = ReplyKeyboardBuilder()
    for i in grades_list:
        kb.button(text=i)
    return kb.as_markup(resize_keyboard=True, input_field_placeholder="Выберите класс")


def settings():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Изменить класс", callback_data="change_class")
    keyboard.button(text="Данные для входа в ЭЖ", callback_data="add_ns")
    keyboard.button(text="Подключить уведомления", callback_data="add_ns_upd")
    keyboard.button(text="Информация о боте", callback_data="info")
    keyboard.button(text="Удалить меня", callback_data="delete_me")
    keyboard.button(text="Стать админом", callback_data='want_to_be_admin')
    keyboard.button(text="Вернуться назад", callback_data="back")
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


def ns():
    kb = InlineKeyboardBuilder()

    for i, day in enumerate(days_list):
        kb.button(text=day, callback_data=str(i))

    kb.button(text="<< Неделя", callback_data="back_week")
    kb.button(text="Назад", callback_data="back")
    kb.button(text="Неделя >>", callback_data="next_week")
    kb.button(text="Домашние задания в боте", callback_data='homework')

    kb.adjust(1, 1, 1, 1, 1, 3, 1)
    return kb.as_markup()


def days(calls: list[str | int], extra_text: str = None):
    kb = InlineKeyboardBuilder()

    for day, call in zip(days_list, calls):
        kb.button(text=day, callback_data=str(call))
    if extra_text:
        kb.button(text=extra_text, callback_data=str(calls[-1]))
    kb.button(text='Назад', callback_data="back")

    kb.adjust(1)
    return kb.as_markup()


def homework_lessons(lessons: List[Lesson], weekday: int, is_admin: bool, edit: bool = False) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for lesson in lessons:
        kb.button(text=lesson.text, callback_data=f'hw_{lesson.id}' if not edit else lesson.id)
    if is_admin and not edit:
        kb.button(text="Добавить ДЗ", callback_data=f'{weekday}_edit_homework')
    kb.button(text='Назад', callback_data="back")
    kb.adjust(1)
    return kb.as_markup()
