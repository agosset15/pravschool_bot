import json
from io import BytesIO
from datetime import datetime

from aiohttp.web_request import Request
from aiohttp.web_response import json_response

from aiogram import Bot, html
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    BufferedInputFile,
    WebAppInfo,
)
from aiogram.utils.web_app import check_webapp_signature, safe_parse_webapp_init_data
from netschoolapi.errors import SchoolNotFoundError, AuthError, NoResponseFromServer

from db.methods.get import get_student_by_telegram_id, get_homework
from db.methods.update import (edit_homework, edit_homework_upd_date, edit_student_login, edit_student_password,
                               edit_student_clas, switch_student_teasher_true, switch_student_duty_notification,
                               switch_student_ns, switch_student_parent)
from db.methods.create import create_homework, create_student
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
    try:
        await ns.login(usr.login, usr.password, 1)
        a = await ns.download_attachment(data['aid'], data['a_id'], data['child'])
        info = await ns.assignment_info(data['a_id'], data['child'])
        await ns.logout()
        await ns.logout()
        await ns.logout()
    except SchoolNotFoundError:
        await ns.logout()
        return json_response({"ok": False, "err": "Internal Server Error"}, status=500)
    except AuthError:
        await ns.logout()
        return json_response({"ok": False, "err": "Internal Server Error"}, status=500)
    await bot.send_document(usr.tgid, BufferedInputFile(a, data['name']),
                            caption=f"{html.bold(info.subjectGroup.name)}\n{info.name}", parse_mode='HTML')
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
    edit_student_clas(usr.tgid, int(data['class']))
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
    try:
        p = await ns.login(data['login'], data['password'], 1)
    except AuthError:
        return json_response({"ok": False, "err": "Неверные данные для ЭЖ"}, status=401)
    st = await ns.students()
    await ns.logout()
    await ns.logout()
    edit_student_login(web_app_init_data.user.id, data['login'])
    edit_student_password(web_app_init_data.user.id, f"{p}")
    switch_student_ns(web_app_init_data.user.id)
    if len(st[0]) > 1:
        switch_student_parent(web_app_init_data.user.id)
    return json_response({'ok': True})


async def register_user(request: Request):
    bot: Bot = request.app['bot']
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
            try:
                p = await ns.login(data['ns_uname'], data['ns_pass'], 1)
            except AuthError:
                return json_response({"ok": False, "err": "Неверные данные для ЭЖ"}, status=401)
            st = await ns.students()
            await ns.logout()
            await ns.logout()
            create_student(web_app_init_data.user.id,
                           f"{web_app_init_data.user.first_name} {web_app_init_data.user.last_name}",
                           web_app_init_data.user.username, int(data['class']), "WebApp")
            edit_student_login(web_app_init_data.user.id, data['ns_uname'])
            edit_student_password(web_app_init_data.user.id, f"{p}")
            switch_student_ns(web_app_init_data.user.id)
            if len(st[0]) > 1:
                switch_student_parent(web_app_init_data.user.id)
            if data['is_tchr'] == 'true':
                switch_student_teasher_true(web_app_init_data.user.id)
            if data['is_noti'] == 'true':
                switch_student_duty_notification(web_app_init_data.user.id)
            return json_response({'ok': True})
    except ValueError:
        try:
            p = await ns.login(data['ns_uname'], data['ns_pass'], 1)
        except AuthError:
            return json_response({"ok": False, "err": "Неверные данные для ЭЖ"}, status=401)
        st = await ns.students()
        await ns.logout()
        await ns.logout()
        create_student(web_app_init_data.user.id,
                       f"{web_app_init_data.user.first_name} {web_app_init_data.user.last_name}",
                       web_app_init_data.user.username, int(data['class']), "WebApp")
        edit_student_login(web_app_init_data.user.id, data['ns_uname'])
        edit_student_password(web_app_init_data.user.id, f"{p}")
        switch_student_ns(web_app_init_data.user.id)
        if len(st[0]) > 1:
            switch_student_parent(web_app_init_data.user.id)
        if data['is_tchr'] == 'true':
            switch_student_teasher_true(web_app_init_data.user.id)
        if data['is_noti'] == 'true':
            switch_student_duty_notification(web_app_init_data.user.id)
        return json_response({'ok': True})
    return json_response({'ok': False, 'err': "Authorized"})
