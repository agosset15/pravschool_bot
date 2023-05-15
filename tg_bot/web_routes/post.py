import json

from datetime import datetime

from aiohttp.web_request import Request
from aiohttp.web_response import json_response

from aiogram import Bot
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent,
    WebAppInfo,
)
from aiogram.utils.web_app import check_webapp_signature, safe_parse_webapp_init_data

from db.methods.get import get_student_by_telegram_id, get_homework
from db.methods.update import edit_homework, edit_homework_upd_date, edit_student_login, edit_student_password, edit_student_clas
from db.methods.create import create_homework


async def check_data_handler(request: Request):
    bot: Bot = request.app["bot"]

    data = await request.post()
    if check_webapp_signature(bot.token, data["_auth"]):
        return json_response({"ok": True})
    return json_response({"ok": False, "err": "Unauthorized"}, status=401)


async def send_message_handler(request: Request):
    bot: Bot = request.app["bot"]
    data = await request.post()
    try:
        web_app_init_data = safe_parse_webapp_init_data(token=bot.token, init_data=data["_auth"])
    except ValueError:
        return json_response({"ok": False, "err": "Unauthorized"}, status=401)

    reply_markup = None
    if data["with_webview"] == "1":
        reply_markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Open",
                        web_app=WebAppInfo(url=str(request.url.with_scheme("https"))),
                    )
                ]
            ]
        )
    await bot.answer_web_app_query(
        web_app_query_id=web_app_init_data.query_id,
        result=InlineQueryResultArticle(
            id=web_app_init_data.query_id,
            title="Demo",
            input_message_content=InputTextMessageContent(
                message_text="Hello, World!",
                parse_mode=None,
            ),
            reply_markup=reply_markup,
        ),
    )
    return json_response({"ok": True})


async def add_db_homework(request: Request):
    bot: Bot = request.app["bot"]
    data = await request.post()
    try:
        web_app_init_data = safe_parse_webapp_init_data(token=bot.token, init_data=data["_auth"])
        usr = get_student_by_telegram_id(int(web_app_init_data.user.id))
    except ValueError:
        return json_response({"ok": False, "err": "Unauthorized"}, status=401)

    if get_homework(int(str(data['lesson'])), usr.clas, int(str(data['day']))) is not None:
        edit_homework(int(str(data['day'])), int(str(data['lesson'])), usr.clas, data['homework'])
        edit_homework_upd_date(int(str(data['day'])), int(str(data['lesson'])), usr.clas,
                               str(datetime.now().strftime('%H:%M %d.%m.%Y')))
    else:
        create_homework(int(str(data['day'])), int(str(data['lesson'])), usr.clas, data['homework'],
                        str(datetime.now().strftime('%H:%M %d.%m.%Y')))
    return json_response({"ok": True})


async def edit_db_class(request: Request):
    full = request.query
    try:
        uusr = full['user']
        clas = full['class']
    except KeyError:
        uusr = full['_auth'].split('&')[1].split('=')[1]
        clas = full['class']
    d = uusr.replace("'", "\"")
    uusr = json.loads(d)
    try:
        usr = get_student_by_telegram_id(int(uusr['id']))
        if usr is None:
            return json_response({"ok": False, "err": "Unauthorized"}, status=401)
    except ValueError:
        return json_response({"ok": False, "err": "Unauthorized"}, status=401)

    edit_student_clas(usr.id, int(clas))
    return json_response({"ok": True})


async def edit_db_ns(request: Request):
    full = request.query
    try:
        uusr = full['user']
        login = full['login']
        password = full['password']
    except KeyError:
        uusr = full['_auth'].split('&')[1].split('=')[1]
        login = full['login']
        password = full['password']
    d = uusr.replace("'", "\"")
    uusr = json.loads(d)
    try:
        usr = get_student_by_telegram_id(int(uusr['id']))
        if usr is None:
            return json_response({"ok": False, "err": "Unauthorized"}, status=401)
    except ValueError:
        return json_response({"ok": False, "err": "Unauthorized"}, status=401)

    edit_student_login(usr.id, login)
    edit_student_password(usr.id, password)
    return json_response({"ok": True})
