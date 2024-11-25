from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardRemove, ForceReply


def inline_kb(adjust=1, switch_text:str = None, switch_param: str = None, **data_text):
    kb = InlineKeyboardBuilder()
    for data, text in data_text.items():
        kb.button(text=text, callback_data=data)
    if switch_text and switch_param:
        kb.button(text=switch_text, switch_inline_query_current_chat=switch_param)
    kb.adjust(adjust)
    return kb.as_markup()


def reply_kb(*texts, placeholder: str = None, adjust=1):
    kb = ReplyKeyboardBuilder()
    for text in texts:
        kb.button(text=text)
    kb.adjust(adjust)
    return kb.as_markup(resize_keyboard=True, input_field_placeholder=placeholder)


def remove_kb():
    return ReplyKeyboardRemove()


def inline_text_attempt(message):
    return ForceReply(input_field_placeholder=message)


def url_kb(adjust=1, **url_text):
    kb = InlineKeyboardBuilder()
    for url, text in url_text.items():
        kb.button(text=text, url=url)
    kb.adjust(adjust)
    return kb.as_markup()


def switch_inline_kb(text: str, param: str):
    kb = InlineKeyboardBuilder()
    kb.button(text=text, switch_inline_query_current_chat=param)

    return kb.as_markup()
