from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultArticle, InlineQueryResult
from aiogram.types import InputTextMessageContent
from db.methods.get import get_student_by_telegram_id
from ..keyboards import keyboards as kb

router = Router()

clases_list = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10б", "10г", "10ф", "11б", "11с", "11ф", "101", "102",
               "103", "111", "112", "113"]


@router.inline_query()
async def inline(query: InlineQuery):
    if query.query in clases_list:
        usersmessage = query.query
        list1 = {'10г': '101', "10е": "102", '10ф': '103', '11г': '111', '11е': '112', '11ф': '113'}
        class_list = ["10г", "10е", "10ф", "11г", "11е", "11ф"]
        if usersmessage in class_list:
            usersmessage = list1[usersmessage]
        await query.answer(kb.inline_kb(int(usersmessage)), cache_time=1, is_personal=True,
                           switch_pm_text="Поговорить лично »»", switch_pm_parameter=f"{usersmessage}_inline")
    elif query.query in ['ns', 'эж', 'ЭЖ', 'NS']:
        usr = get_student_by_telegram_id(query.from_user.id)
        if usr:
            try:
                clas = usr.clas
                if clas > 0:
                    await query.answer(await kb.inline_ns_kb(usr), cache_time=86400, is_personal=True,
                                       switch_pm_text="Поговорить лично »»", switch_pm_parameter="inline")
                else:
                    buttons = [
                        InlineQueryResultArticle(id="err", title="Вы не зарегистрированы!",
                                                 description="Зарегистрируйтесь по кнопке выше, или напишите класс",
                                                 input_message_content=InputTextMessageContent(message_text='Ошибка!'))]
                    await query.answer(buttons, cache_time=1, switch_pm_parameter="inline",
                                       switch_pm_text="Регистрация »»")
            except TypeError:
                buttons = [
                    InlineQueryResultArticle(id="err", title="Вы не зарегистрированы!",
                                             description="Зарегистрируйтесь по кнопке выше, или напишите класс",
                                             input_message_content=InputTextMessageContent(message_text='Ошибка!'))]
                await query.answer(buttons, cache_time=1, switch_pm_parameter="inline", switch_pm_text="Регистрация »»")
        else:
            buttons = [
                InlineQueryResultArticle(id="err", title="Вы не зарегистрированы!",
                                         description="Зарегистрируйтесь по кнопке выше, или напишите класс",
                                         input_message_content=InputTextMessageContent(message_text='Ошибка!'))]
            await query.answer(buttons, cache_time=1, switch_pm_parameter="inline", switch_pm_text="Регистрация »»")
    else:
        usr = get_student_by_telegram_id(query.from_user.id)
        if usr:
            try:
                clas = usr.clas
                if usr.isTeacher is True:
                    await query.answer(kb.inline_kb(clas=None, uch=clas), cache_time=1, is_personal=True,
                                       switch_pm_text="Поговорить лично »»", switch_pm_parameter="inline")
                elif clas > 0:
                    await query.answer(kb.inline_kb(clas), cache_time=1, is_personal=True,
                                       switch_pm_text="Поговорить лично »»", switch_pm_parameter="inline")
                else:
                    buttons = [
                        InlineQueryResultArticle(id="err", title="Вы не зарегистрированы!",
                                                 description="Зарегистрируйтесь по кнопке выше, или напишите класс",
                                                 input_message_content=InputTextMessageContent(message_text='Ошибка!'))]
                    await query.answer(buttons, cache_time=1, switch_pm_parameter="inline",
                                       switch_pm_text="Регистрация »»")
            except TypeError:
                buttons = [
                    InlineQueryResultArticle(id="err", title="Вы не зарегистрированы!",
                                             description="Зарегистрируйтесь по кнопке выше, или напишите класс",
                                             input_message_content=InputTextMessageContent(message_text='Ошибка!'))]
                await query.answer(buttons, cache_time=1, switch_pm_parameter="inline", switch_pm_text="Регистрация »»")
        else:
            buttons = [
                InlineQueryResultArticle(id="err", title="Вы не зарегистрированы!",
                                         description="Зарегистрируйтесь по кнопке выше, или напишите класс",
                                         input_message_content=InputTextMessageContent(message_text='Ошибка!'))]
            await query.answer(buttons, cache_time=1, switch_pm_parameter="inline", switch_pm_text="Регистрация »»")
