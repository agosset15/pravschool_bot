from aiogram import types
from db import Database

db = Database("rs-bot.db", 'users.db')


def get_startkeyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["📕ПОНЕДЕЛЬНИК📕", "📗ВТОРНИК📗", "📘СРЕДА📘", "📙ЧЕТВЕРГ📙", "📔ПЯТНИЦА📔", "📚ОСОБОЕ МЕНЮ📚"]
    keyboard.add(*buttons)
    return keyboard


def inline_kb(clas: int or None, uch: int | None = None):
    if clas is not None:
        arr = db.week(clas)
        buttons = [
            types.InlineQueryResultArticle(id="1", title="📕ПОНЕДЕЛЬНИК📕",
                                           input_message_content=types.InputTextMessageContent(arr[0])),
            types.InlineQueryResultArticle(id="2", title="📗ВТОРНИК📗",
                                           input_message_content=types.InputTextMessageContent(arr[1])),
            types.InlineQueryResultArticle(id="3", title="📘СРЕДА📘",
                                           input_message_content=types.InputTextMessageContent(arr[2])),
            types.InlineQueryResultArticle(id="4", title="📙ЧЕТВЕРГ📙",
                                           input_message_content=types.InputTextMessageContent(arr[3])),
            types.InlineQueryResultArticle(id="5", title="📔ПЯТНИЦА📔",
                                           input_message_content=types.InputTextMessageContent(arr[4]))
        ]
        return buttons
    else:
        arr = db.teacher_week(uch)
        buttons = [
            types.InlineQueryResultArticle(id="1", title="📕ПОНЕДЕЛЬНИК📕",
                                           input_message_content=types.InputTextMessageContent(arr[0])),
            types.InlineQueryResultArticle(id="2", title="📗ВТОРНИК📗",
                                           input_message_content=types.InputTextMessageContent(arr[1])),
            types.InlineQueryResultArticle(id="3", title="📘СРЕДА📘",
                                           input_message_content=types.InputTextMessageContent(arr[2])),
            types.InlineQueryResultArticle(id="4", title="📙ЧЕТВЕРГ📙",
                                           input_message_content=types.InputTextMessageContent(arr[3])),
            types.InlineQueryResultArticle(id="5", title="📔ПЯТНИЦА📔",
                                           input_message_content=types.InputTextMessageContent(arr[4]))
        ]
        return buttons


def vip_menu():
    buttons = [
        types.InlineKeyboardButton(text="Изменить расписание",
                                   callback_data="new_rasp"),
        types.InlineKeyboardButton(text="Назначить админа",
                                   callback_data="admin_add"),
        types.InlineKeyboardButton(text="Сводка пользователей",
                                   callback_data="users_check"),
        types.InlineKeyboardButton(text="Error_log",
                                   callback_data="log"),
        types.InlineKeyboardButton(text="Сделать объявление",
                                   callback_data="ad")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard


def admin_menu():
    buttons = [
        types.InlineKeyboardButton(text="Изменить расписание",
                                   callback_data="new_rasp"),
        types.InlineKeyboardButton(text="Сделать объявление",
                                   callback_data="ad")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard


def sp_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["📖НА НЕДЕЛЮ📖", "📚НА ГОД📚", "⚙️Настройки⚙️"]
    keyboard.add(*buttons)
    return keyboard


def inboard():
    buttons = [
        types.InlineKeyboardButton(text="Расписание на сегодня", callback_data="now"),
        types.InlineKeyboardButton(text="Расписание на завтра", callback_data="tom")]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard


def uinb():
    buttons = [
        types.InlineKeyboardButton(text="Расписание на сегодня", callback_data="now"),
        types.InlineKeyboardButton(text="Расписание на завтра", callback_data="tom"),
        types.InlineKeyboardButton(text="Расписание по кабинетам", callback_data="kab")]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard


def uchitel():
    button = types.InlineKeyboardButton(text="Я-учитель👨‍🏫", callback_data="uch")
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(button)
    return keyboard


def settings():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Изменить класс", "меню отладки(для разработчика)"]
    keyboard.add(*buttons)
    return keyboard


def clases():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=6)
    buttons = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10б", "10г", "10ф", "11б", "11с", "11ф"]
    keyboard.add(*buttons)
    return keyboard


def rem():
    rem = types.ReplyKeyboardRemove()
    return rem
