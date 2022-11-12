from aiogram import Router, F
from aiogram.types import InlineQuery, InlineQueryResultArticle
from aiogram.types.input_text_message_content import InputTextMessageContent
from pravschool_bot.db import Database
from pravschool_bot.keyboards import keyboards as kb

router = Router()
db = Database("rs-bot.db", 'users.db')

clases_list = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10б", "10г", "10ф", "11б", "11с", "11ф"]


@router.inline_query()
async def inline(query: InlineQuery):
    if query.query in clases_list:
        usersmessage = query.query
        list1 = {'10б': '101', "10г": "102", '10ф': '103', '11б': '111', '11с': '112', '11ф': '113'}
        class_list = ["10б", "10г", "10ф", "11б", "11с", "11ф"]
        if usersmessage in class_list:
            usersmessage = list1[usersmessage]
        await query.answer(kb.inline_kb(int(usersmessage)), cache_time=1, is_personal=True,
                           switch_pm_text="Поговорить лично »»", switch_pm_parameter=f"{query.query}_inline")
    else:
        us = db.user_exists(query.from_user.id)
        if us is True:
            try:
                uh = db.teacher(query.from_user.id)
                cls = db.what_class(query.from_user.id)
                if cls != 0:
                    await query.answer(kb.inline_kb(cls), cache_time=1, is_personal=True,
                                       switch_pm_text="Поговорить лично »»", switch_pm_parameter="ls_inline")
                if uh in range(1, 40):
                    await query.answer(kb.inline_kb(clas=None, uch=uh), cache_time=1, is_personal=True,
                                       switch_pm_text="Поговорить лично »»", switch_pm_parameter="ls_inline")
            except TypeError:
                cont = InputTextMessageContent(
                    message_text=("Ошибка!\nВы не зарегистрированы. \nЗарегистрируйтесь в лс "
                                  "бота."))
                buttons = [
                    InlineQueryResultArticle(id="err", title="Вы не зарегистрированы!",
                                             description="Зарегистрируйтесь по кнопке выше, или напишите класс",
                                             input_message_content=cont)]
                await query.answer(buttons, cache_time=1, switch_pm_parameter="inline", switch_pm_text="Регистрация »»")
        else:
            cont = InputTextMessageContent(message_text=("Ошибка!\nВы не зарегистрированы. \nЗарегистрируйтесь в лс "
                                                         "бота."))
            buttons = [
                InlineQueryResultArticle(id="err", title="Вы не зарегистрированы!",
                                         description="Зарегистрируйтесь по кнопке выше, или напишите класс",
                                         input_message_content=cont)]
            await query.answer(buttons, cache_time=1, switch_pm_parameter="inline", switch_pm_text="Регистрация »»")
