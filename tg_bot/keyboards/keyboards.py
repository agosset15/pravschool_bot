import ast
from aiogram import types, html
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder, InlineKeyboardButton, \
    InlineKeyboardMarkup
from db.methods.get import get_schedule, get_teacher_schedule
from db import Student
from ..config import ns
from netschoolapi.errors import SchoolNotFoundError, AuthError


def get_startkeyboard() -> types.ReplyKeyboardMarkup:
    buttons = ["ПОНЕДЕЛЬНИК", "ВТОРНИК", "СРЕДА", "ЧЕТВЕРГ", "ПЯТНИЦА", "ОСОБОЕ МЕНЮ"]
    kb = ReplyKeyboardBuilder()
    for i in buttons:
        kb.button(text=i)
    kb.adjust(3)
    return kb.as_markup(resize_keyboard=True, input_field_placeholder="Нажмите на кнопку ниже")


def days_inline() -> types.InlineKeyboardMarkup:
    buttons = ["ПОНЕДЕЛЬНИК", "ВТОРНИК", "СРЕДА", "ЧЕТВЕРГ", "ПЯТНИЦА"]
    kb = InlineKeyboardBuilder()
    kb.button(text=buttons[0], callback_data='mon')
    kb.button(text=buttons[1], callback_data='tue')
    kb.button(text=buttons[2], callback_data='wed')
    kb.button(text=buttons[3], callback_data='thu')
    kb.button(text=buttons[4], callback_data='fri')
    kb.button(text='Назад', callback_data="back")
    kb.adjust(1)
    return kb.as_markup()


def hw_lessons(user, wday, adm: bool) -> types.InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    day = ast.literal_eval(get_schedule(user.clas, wday))
    for i, l in day, range(0, len(day) - 1):
        kb.button(text=i, callback_data=f'hw_{l}_{wday}')
    if adm:
        kb.button(text="Добавить ДЗ", callback_data=f'{wday}_edit_homework')
    kb.button(text='Назад', callback_data="back")
    kb.adjust(1)
    return kb.as_markup()


def inline_kb(clas: int | None, uch: int = None):
    week = ""
    if clas is not None:
        arr = []
        for i in range(1, 6):
            arr.append('\n'.join(ast.literal_eval(get_schedule(clas, i))))
    else:
        arr = []
        for i in range(1, 6):
            arr.append('\n'.join(ast.literal_eval(get_teacher_schedule(uch, i))))
    week = (f"<b>Понедельник:</b>\n{arr[0]}\n\n<b>Вторник:</b>\n{arr[1]}\n\n<b>Среда:</b>\n{arr[2]}"
            f"\n\n<b>Четверг:</b>\n{arr[3]}\n\n<b>Пятница:</b>\n{arr[4]}")
    buttons = [
        types.InlineQueryResultArticle(id="1", title="ПОНЕДЕЛЬНИК",
                                       input_message_content=types.InputTextMessageContent(message_text=arr[0]),
                                       reply_markup=url_kb("https://t.me/pravschool_bot?start=inline_button"),
                                       thumbnail_url="https://i.postimg.cc/Rh06vDF8/mon.png", thumbnail_height=512,
                                       thumbnail_width=512),
        types.InlineQueryResultArticle(id="2", title="ВТОРНИК",
                                       input_message_content=types.InputTextMessageContent(message_text=arr[1]),
                                       reply_markup=url_kb("https://t.me/pravschool_bot?start=inline_button")),
        types.InlineQueryResultArticle(id="3", title="СРЕДА",
                                       input_message_content=types.InputTextMessageContent(message_text=arr[2]),
                                       reply_markup=url_kb("https://t.me/pravschool_bot?start=inline_button")),
        types.InlineQueryResultArticle(id="4", title="ЧЕТВЕРГ",
                                       input_message_content=types.InputTextMessageContent(message_text=arr[3]),
                                       reply_markup=url_kb("https://t.me/pravschool_bot?start=inline_button")),
        types.InlineQueryResultArticle(id="5", title="ПЯТНИЦА",
                                       input_message_content=types.InputTextMessageContent(message_text=arr[4]),
                                       reply_markup=url_kb("https://t.me/pravschool_bot?start=inline_button")),
        types.InlineQueryResultArticle(id="6", title="На неделю",
                                       input_message_content=types.InputTextMessageContent(message_text=week,
                                                                                           parse_mode='HTML'),
                                       reply_markup=url_kb("https://t.me/pravschool_bot?start=inline_button"))
    ]
    return buttons


async def inline_ns_kb(usr: Student):
    arr = []
    try:
        await ns.login(usr.login, usr.password, 'Свято-Димитриевская школа')
        diary = await ns.diary()
        await ns.logout()
        await ns.logout()
        await ns.logout()
        day = diary.schedule
    except SchoolNotFoundError or AuthError:
        await ns.logout()
        err = [types.InlineQueryResultArticle(id="err", title="Неверный логин/пароль.",
                                              description="Измените их пожалуйста в ЛС. Кнопка выше.")]
        return err
    for da in day:
        lesson = da.lessons
        message_text = []
        for less in lesson:
            assig = less.assignments
            if assig:
                for i in assig:
                    if i.mark is None:
                        if i.is_duty is True:
                            message_text.append(
                                f"⚠️ДОЛГ!\n{html.bold(i.type)}({less.subject})\n{i.content}")
                        else:
                            message_text.append(f"{html.bold(i.type)}({less.subject})\n{i.content}")
                    else:
                        message_text.append(
                            f"{html.bold(i.type)}({less.subject})\n{i.content} -- {html.bold(i.mark)}")
            else:
                message_text.append(f"{html.bold(less.subject)}\nЗаданий нет.")
        msg = "\n\n".join(message_text)
        arr.append(msg)

    buttons = [
        types.InlineQueryResultArticle(id="1", title="ПОНЕДЕЛЬНИК",
                                       input_message_content=types.InputTextMessageContent(message_text=arr[0],
                                                                                           parse_mode='HTML')),
        types.InlineQueryResultArticle(id="2", title="ВТОРНИК",
                                       input_message_content=types.InputTextMessageContent(message_text=arr[1],
                                                                                           parse_mode='HTML')),
        types.InlineQueryResultArticle(id="3", title="СРЕДА",
                                       input_message_content=types.InputTextMessageContent(message_text=arr[2],
                                                                                           parse_mode='HTML')),
        types.InlineQueryResultArticle(id="4", title="ЧЕТВЕРГ",
                                       input_message_content=types.InputTextMessageContent(message_text=arr[3],
                                                                                           parse_mode='HTML')),
        types.InlineQueryResultArticle(id="5", title="ПЯТНИЦА",
                                       input_message_content=types.InputTextMessageContent(message_text=arr[4],
                                                                                           parse_mode='HTML'))
    ]
    return buttons


def vip_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="Изменить расписание", callback_data="new_rasp")
    kb.button(text="Добавление фото", callback_data="photo_add")
    kb.button(text="Назначить админа", callback_data="admin_add")
    kb.button(text="Сводка пользователей", callback_data="users_check")
    kb.button(text="Удалить пользователя", callback_data="del_user")
    kb.button(text="Сделать объявление", callback_data="ad")
    kb.adjust(1)
    return kb.as_markup()


def sqlite_upd():
    kb = InlineKeyboardBuilder()
    kb.button(text="Получить файл", callback_data="sql_upd")
    kb.adjust(1)
    return kb.as_markup()


def uinb():
    buttons = [
        [InlineKeyboardButton(text="Расписание на сегодня", callback_data="now")],
        [InlineKeyboardButton(text="Расписание на завтра", callback_data="tom")],
        [InlineKeyboardButton(text="Расписание по кабинетам", callback_data="kab")],
        [
            InlineKeyboardButton(text="На неделю", callback_data="week"),
            InlineKeyboardButton(text="На год", callback_data="year"),
            InlineKeyboardButton(text="ЭЖ", callback_data="ns"),
            InlineKeyboardButton(text="Настройки", callback_data="settings")],
        [InlineKeyboardButton(text="Домашнее задание", callback_data="homework")],
        [InlineKeyboardButton(text="Веб интерфейс",
                              web_app=types.WebAppInfo(url='https://tg.ag15.ru/demo?nextpage=1'))],
        [InlineKeyboardButton(text="Попробовать в любом чате",
                              switch_inline_query_chosen_chat=types.SwitchInlineQueryChosenChat(allow_bot_chats=False,
                                                                                                allow_user_chats=True,
                                                                                                allow_channel_chats=True,
                                                                                                allow_group_chats=True))]
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
    keyboard.button(text="Подключить ЭЖ", callback_data="add_ns")
    keyboard.button(text="Подключить уведомления", callback_data="add_ns_upd")
    keyboard.button(text="Информация о боте", callback_data="info")
    keyboard.button(text="Удалить меня", callback_data="delete")
    keyboard.button(text="Стать админом", callback_data='wanttobeadmin')
    keyboard.button(text="Вернуться назад", callback_data="back")
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


def ns_settings():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Изменить логин/пароль", callback_data="change_ns")
    keyboard.button(text="Вернуться назад", callback_data="back")
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)


def clases():
    kb = ReplyKeyboardBuilder()
    buttons = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10г", "10е", "10ф", "11г", "11е", "11ф"]
    for i in buttons:
        kb.button(text=i)
    return kb.as_markup(resize_keyboard=True, input_field_placeholder="Выберете свой класс")


def rasp_kb(arr: list):
    kb = InlineKeyboardBuilder()
    for i in range(1, len(arr) + 1):
        kb.button(text=arr[i - 1], callback_data=f"{i}")
    kb.adjust(1)
    return kb.as_markup()


def admin_kb(day):
    kb = InlineKeyboardBuilder()
    kb.button(text="Добавить ДЗ", callback_data=f'{day}_edit_homework')
    kb.button(text="Назад", callback_data='back')
    kb.adjust(1)
    return kb.as_markup()


def back():
    kb = InlineKeyboardBuilder()
    kb.button(text="Назад", callback_data='back')
    kb.adjust(1)
    return kb.as_markup()


def url_kb(url: str):
    kb = InlineKeyboardBuilder()
    kb.button(text="Все расписание", url=url)
    kb.adjust(1)
    return kb.as_markup()


def reply_rext_kb(text: str, placeholder: str = None):
    kb = ReplyKeyboardBuilder()
    kb.button(text=text)
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True, input_field_placeholder=placeholder)


def make_ns():
    buttons = ["ПОНЕДЕЛЬНИК", "ВТОРНИК", "СРЕДА", "ЧЕТВЕРГ", "ПЯТНИЦА"]
    buttons = [
        [InlineKeyboardButton(text=buttons[0], callback_data='0')],
        [InlineKeyboardButton(text=buttons[1], callback_data='1')],
        [InlineKeyboardButton(text=buttons[2], callback_data='2')],
        [InlineKeyboardButton(text=buttons[3], callback_data='3')],
        [InlineKeyboardButton(text=buttons[4], callback_data='4')],
        [
            InlineKeyboardButton(text="<< Неделя", callback_data="back_week"),
            InlineKeyboardButton(text="Назад", callback_data="back"),
            InlineKeyboardButton(text="Неделя >>", callback_data="next_week")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def extract_unique_code(text):
    return text.split()[1] if len(text.split()) > 1 else None


def rem():
    remq = types.ReplyKeyboardRemove()
    return remq
