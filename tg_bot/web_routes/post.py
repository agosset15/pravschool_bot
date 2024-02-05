import json
from io import BytesIO
from datetime import datetime

from aiohttp.web_request import Request
from aiohttp.web_response import json_response

from aiogram import Bot
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    BufferedInputFile,
    WebAppInfo,
)
from aiogram.utils.web_app import check_webapp_signature, safe_parse_webapp_init_data
from netschoolapi.errors import SchoolNotFoundError, AuthError, NoResponseFromServer

from db.methods.get import get_student_by_telegram_id, get_homework
from db.methods.update import edit_homework, edit_homework_upd_date, edit_student_login, edit_student_password, edit_student_clas
from db.methods.create import create_homework
from ..config import MyEncoder, ns


async def send_message_handler(request: Request):
    bot: Bot = request.app["bot"]
    data = await request.post()
    if not (check_webapp_signature(bot.token, data["_auth"])):
        return json_response({"ok": False, "err": "Unauthorized"}, status=401)
    try:
        web_app_init_data = safe_parse_webapp_init_data(token=bot.token, init_data=data["_auth"])
    except ValueError:
        return json_response({"ok": False, "err": "Unauthorized"}, status=401)
    try:
        usr = get_student_by_telegram_id(web_app_init_data.user.id)
        if usr is None:
            return json_response({"ok": False, "err": "Unauthorized"}, status=401)
    except ValueError:
        return json_response({"ok": False, "err": "Unauthorized"}, status=401)
    io = BytesIO()
    try:
        await ns.login(usr.login, usr.password)
        await ns.download_attachment(data['a_id'], io)
        await ns.logout()
        await ns.logout()
        await ns.logout()
    except SchoolNotFoundError:
        await ns.logout()
        return json_response({"ok": False, "err": "Internal Server Error"}, status=500)
    except AuthError:
        await ns.logout()
        return json_response({"ok": False, "err": "Internal Server Error"}, status=500)

    await bot.send_document(usr.tgid, BufferedInputFile(io.read(), data['name']))
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
        edit_homework(int(str(data['day'])), int(str(data['lesson'])), usr.clas, data['homework'], None)
        edit_homework_upd_date(int(str(data['day'])), int(str(data['lesson'])), usr.clas,
                               str(datetime.now().strftime('%H:%M %d.%m.%Y')))
    else:
        create_homework(int(str(data['day'])), int(str(data['lesson'])), usr.clas, data['homework'],
                        str(datetime.now().strftime('%H:%M %d.%m.%Y')))
    return json_response({"ok": True})


async def edit_db_class(request: Request):
    bot: Bot = request.app["bot"]
    data = request.query
    if not (check_webapp_signature(bot.token, data["_auth"])):
        return json_response({"ok": False, "err": "Unauthorized"}, status=401)
    try:
        web_app_init_data = safe_parse_webapp_init_data(token=bot.token, init_data=data["_auth"])
    except ValueError:
        return json_response({"ok": False, "err": "Unauthorized"}, status=401)
    try:
        usr = get_student_by_telegram_id(web_app_init_data.user.id)
        if usr is None:
            return json_response({"ok": False, "err": "Unauthorized"}, status=401)
    except ValueError:
        return json_response({"ok": False, "err": "Unauthorized"}, status=401)

    edit_student_clas(usr.id, int(data['class']))
    return json_response({"ok": True})


async def edit_db_ns(request: Request):
    bot: Bot = request.app["bot"]
    data = request.query
    if not (check_webapp_signature(bot.token, data["_auth"])):
        return json_response({"ok": False, "err": "Unauthorized"}, status=401)
    try:
        web_app_init_data = safe_parse_webapp_init_data(token=bot.token, init_data=data["_auth"])
    except ValueError:
        return json_response({"ok": False, "err": "Unauthorized"}, status=401)
    try:
        usr = get_student_by_telegram_id(web_app_init_data.user.id)
        if usr is None:
            return json_response({"ok": False, "err": "Unauthorized"}, status=401)
    except ValueError:
        return json_response({"ok": False, "err": "Unauthorized"}, status=401)
    edit_student_login(usr.id, data['login'])
    edit_student_password(usr.id, data['password'])
    return json_response({"ok": True})
