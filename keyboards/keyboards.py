from typing import Optional, Union
from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder, InlineKeyboardButton,\
    InlineKeyboardMarkup
from ..db import Database

db = Database("rs-bot.db", 'users.db')


def get_startkeyboard() -> types.ReplyKeyboardMarkup:
    buttons = ["ПОНЕДЕЛЬНИК", "ВТОРНИК", "СРЕДА", "ЧЕТВЕРГ", "ПЯТНИЦА", "ОСОБОЕ МЕНЮ"]
    kb = ReplyKeyboardBuilder()
    for i in buttons:
        kb.button(text=i)
    kb.adjust(3)
    return kb.as_markup(resize_keyboard=True, input_field_placeholder="Нажмите на кнопку ниже")


def inline_kb(clas: Union[int, None], uch: Optional[int] = None):
    if clas is not None:
        arr = db.week(clas)
    else:
        arr = db.teacher_week(uch)
    buttons = [
        types.InlineQueryResultArticle(id="1", title="ПОНЕДЕЛЬНИК",
                                       input_message_content=types.InputTextMessageContent(message_text=arr[0])),
        types.InlineQueryResultArticle(id="2", title="ВТОРНИК",
                                       input_message_content=types.InputTextMessageContent(message_text=arr[1])),
        types.InlineQueryResultArticle(id="3", title="СРЕДА",
                                       input_message_content=types.InputTextMessageContent(message_text=arr[2])),
        types.InlineQueryResultArticle(id="4", title="ЧЕТВЕРГ",
                                       input_message_content=types.InputTextMessageContent(message_text=arr[3])),
        types.InlineQueryResultArticle(id="5", title="ПЯТНИЦА",
                                       input_message_content=types.InputTextMessageContent(message_text=arr[4]))
    ]
    return buttons


def vip_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="Изменить расписание", callback_data="new_rasp")
    kb.button(text="Добавление фото", callback_data="photo_add")
    kb.button(text="Назначить админа", callback_data="admin_add")
    kb.button(text="Сводка пользователей", callback_data="users_check")
    kb.button(text="Удалить пользователя", callback_data="del_user")
    kb.button(text="Error_log", callback_data="log")
    kb.button(text="Сделать объявление", callback_data="ad")
    kb.adjust(1)
    return kb.as_markup()


def admin_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="Изменить расписание", callback_data="new_rasp")
    kb.button(text="Сделать объявление", callback_data="ad")
    return kb.as_markup()


def uinb():
    buttons = [
        [InlineKeyboardButton(text="Расписание на сегодня", callback_data="now")],
        [InlineKeyboardButton(text="Расписание на завтра", callback_data="tom")],
        [InlineKeyboardButton(text="Расписание по кабинетам", callback_data="kab")],
        [
            InlineKeyboardButton(text="На неделю", callback_data="week"),
            InlineKeyboardButton(text="На год", callback_data="year"),
            InlineKeyboardButton(text="Настройки", callback_data="settings")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def uchitel():
    kb = InlineKeyboardBuilder()
    kb.button(text="Я-учитель👨‍🏫", callback_data="uch")
    return kb.as_markup()


def settings():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Изменить класс", callback_data="change_class")
    keyboard.button(text="Информация о боте", callback_data="info")
    keyboard.button(text="Удалить меня", callback_data="delete")
    keyboard.button(text="Вернуться назад", callback_data="back")
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


def clases():
    kb = ReplyKeyboardBuilder()
    buttons = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10б", "10г", "10ф", "11б", "11с", "11ф"]
    for i in buttons:
        kb.button(text=i)
    return kb.as_markup(resize_keyboard=True, input_field_placeholder="Выберете свой класс")


def extract_unique_code(text):
    return text.split()[1] if len(text.split()) > 1 else None


def rem():
    remq = types.ReplyKeyboardRemove()
    return remq
