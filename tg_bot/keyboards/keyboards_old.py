from aiogram.utils.keyboard import InlineKeyboardBuilder


def rasp_kb(arr: list):
    kb = InlineKeyboardBuilder()
    for i in range(1, len(arr)):
        kb.button(text=arr[i - 1], callback_data=f"{i}")
    kb.adjust(1)
    return kb.as_markup()


def admin_kb(day):
    kb = InlineKeyboardBuilder()
    kb.button(text="Добавить ДЗ", callback_data=f'{day}_edit_homework')
    kb.button(text="Назад", callback_data='back')
    kb.adjust(1)
    return kb.as_markup()


def url_kb(url: str):
    kb = InlineKeyboardBuilder()
    kb.button(text="Все расписание", url=url)
    kb.adjust(1)
    return kb.as_markup()
