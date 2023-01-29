from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultArticle
from aiogram.types.input_text_message_content import InputTextMessageContent
from db.methods.get import get_student_by_telegram_id
from ..keyboards import keyboards as kb

router = Router()

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
                           switch_pm_text="Поговорить лично »»", switch_pm_parameter=f"{usersmessage}_inline")
    else:
        usr = get_student_by_telegram_id(query.from_user.id)
        if usr == 1:
            try:
                clas = usr.clas
                if clas != 0:
                    await query.answer(kb.inline_kb(clas), cache_time=1, is_personal=True,
                                       switch_pm_text="Поговорить лично »»", switch_pm_parameter="inline")
                if usr.isTeacher == 1:
                    await query.answer(kb.inline_kb(clas=None, uch=clas), cache_time=1, is_personal=True,
                                       switch_pm_text="Поговорить лично »»", switch_pm_parameter="inline")
                else:
                    cont = InputTextMessageContent(
                        message_text=("Ошибка!\nВы не зарегистрированы. \nЗарегистрируйтесь в лс "
                                      "бота."))
                    buttons = [
                        InlineQueryResultArticle(id="err", title="Вы не зарегистрированы!",
                                                 description="Зарегистрируйтесь по кнопке выше, или напишите класс",
                                                 input_message_content=cont)]
                    await query.answer(buttons, cache_time=1, switch_pm_parameter="inline",
                                       switch_pm_text="Регистрация »»")
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