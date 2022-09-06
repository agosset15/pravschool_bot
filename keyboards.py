from aiogram import types


def get_startkeyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["📕ПОНЕДЕЛЬНИК📕", "📗ВТОРНИК📗", "📘СРЕДА📘", "📙ЧЕТВЕРГ📙", "📔ПЯТНИЦА📔", "📚ОСОБОЕ МЕНЮ📚"]
    keyboard.add(*buttons)
    return keyboard


def vip_menu():
    buttons = [
        types.InlineKeyboardButton(text="Изменить расписание",
                                   callback_data="edit"),
        types.InlineKeyboardButton(text="Сделать объявление",
                                   callback_data="ad")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard


def sp_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["📖РАСПИСАНИЕ НА НЕДЕЛЮ📖", "⚙️Настройки⚙️"]
    keyboard.add(*buttons)
    return keyboard


def inboard():
    buttons = [
        types.InlineKeyboardButton(text="Расписание на сегодня.", callback_data="now"),
        types.InlineKeyboardButton(text="Расписание на завтра", callback_data="tom")]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard


def uchitel():
    button = types.InlineKeyboardButton(text="Я-учитель👨‍🏫", callback_data="uch")
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(button)
    return keyboard


def bots_list():
    buttons = [
        types.InlineKeyboardButton(text="Бот - казино",
                                   url="tg://resolve?domain=Ice_Cazino_bot"),
        types.InlineKeyboardButton(text="Бот по продаже услуг",
                                   url="tg://resolve?domain=SellServices_bot"),
        types.InlineKeyboardButton(text="Бот по TERMUXу, и еще много чему",
                                   url="tg://resolve?domain=BotickforTermux_bot"),
        types.InlineKeyboardButton(text="Канал по софтам",
                                   url="tg://resolve?domain=Kiberhack"),
        types.InlineKeyboardButton(text="Бот для взлома пентагона, ФСБ, ФБР",
                                   url="tg://resolve?domain=Vzlombotik123_bot")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


def settings():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Изменить класс", "меню отладки(для разработчика)"]
    keyboard.add(*buttons)
    return keyboard


def napr10():
    buttons = [
        types.InlineKeyboardButton(text="Физико-техническое", callback_data="f"),
        types.InlineKeyboardButton(text="Социальное", callback_data="s"),
        types.InlineKeyboardButton(text="Биолого-химическое", callback_data="b")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard


def napr11():
    buttons = [
        types.InlineKeyboardButton(text="Физико-техническое", callback_data="f"),
        types.InlineKeyboardButton(text="Социальное", callback_data="s"),
        types.InlineKeyboardButton(text="Гуманитарное", callback_data="b")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
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
