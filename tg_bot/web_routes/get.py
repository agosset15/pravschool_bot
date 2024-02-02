import ast
import json
import datetime
from pathlib import Path

from aiogram.utils.web_app import safe_parse_webapp_init_data, check_webapp_signature
from aiohttp.web_fileresponse import FileResponse
from aiohttp.web_request import Request
from aiohttp.web_response import json_response
from netschoolapi.errors import SchoolNotFoundError, AuthError, NoResponseFromServer

from db.methods.get import (get_student_by_telegram_id,
                            get_schedule, get_homework,
                            get_teacher_schedule,
                            get_kab_schedule, get_count)
from ..config import MyEncoder, ns


async def demo_handler(request: Request):
    full = request.query
    try:
        if int(full['nextpage']) == 2:
            return FileResponse(Path(__file__).parent.resolve() / "profile.html")
        elif int(full['nextpage']) == 1:
            return FileResponse(Path(__file__).parent.resolve() / "demo.html")
        else:
            return json_response({"ok": False, "err": "Not Found"}, status=404)
    except:
        return json_response({"ok": False, "err": "Not Found"}, status=404)


async def getdb_user(request: Request):
    full = request.query
    bot: Bot = request.app["bot"]
    if not (check_webapp_signature(bot.token, full["_auth"])):
        return json_response({"ok": False, "err": "Unauthorized"}, status=401)
    try:
        web_app_init_data = safe_parse_webapp_init_data(token=bot.token, init_data=full["_auth"])
    except ValueError:
        return json_response({"ok": False, "err": "Unauthorized"}, status=401)
    try:
        usr = get_student_by_telegram_id(web_app_init_data.user.id)
        if usr is None:
            return json_response({"ok": False, "err": "Unauthorized"}, status=401)
    except ValueError:
        return json_response({"ok": False, "err": "Unauthorized"}, status=401)

    classs = usr.clas
    print(classs)
    class_list = [101, 102, 103, 111, 112, 113]
    list1 = {101: '10г', 102: "10е", 103: '10ф', 111: '11г', 112: '11е', 113: '11ф'}
    if classs in class_list:
        classs = list1[classs]
    return json_response(
        {'ok': True, 'name': usr.name, 'clas': classs, 'id': usr.id, 'isTeacher': usr.isTeacher, 'isNs': usr.isNs,
         'ntf': usr.duty_notification, 'isAdmin': usr.isAdmin, 'pass': usr.password, 'login': usr.login})


async def getdb_rasp(request: Request):
    full = request.query
    try:
        uusr = full['user']
    except KeyError:
        uusr = full['_auth'].split('&')[1].split('=')[1]
    d = uusr.replace("'", "\"")
    uusr = json.loads(d)
    try:
        usr = get_student_by_telegram_id(int(uusr['id']))
        if usr is None:
            return json_response({"ok": False, "err": "Unauthorized"}, status=401)
    except ValueError:
        print('ERROR')
        return json_response({"ok": False, "err": "Unauthorized"}, status=401)
    if usr.isTeacher is True:
        rasp = get_teacher_schedule(usr.clas, int(full['day']))
    else:
        rasp = get_schedule(usr.clas, int(full['day']))
    res = '\n'.join(ast.literal_eval(rasp))
    return json_response({'ok': True, 'rasp': res})


async def getdb_homework(request: Request):
    full = request.query
    try:
        uusr = full['user']
    except KeyError:
        uusr = full['_auth'].split('&')[1].split('=')[1]
    d = uusr.replace("'", "\"")
    uusr = json.loads(d)
    try:
        usr = get_student_by_telegram_id(int(uusr['id']))
        if usr is None:
            return json_response({"ok": False, "err": "Unauthorized"}, status=401)
    except ValueError:
        return json_response({"ok": False, "err": "Unauthorized"}, status=401)

    day = ast.literal_eval(get_schedule(usr.clas, int(full['day'])))
    homework = []
    for i in range(1, len(day) + 1):
        hm = get_homework(i, usr.clas, int(full['day']))
        if hm is None:
            homework.append(f"#<b>{day[i - 1]}</b> - Нет")
        else:
            homework.append(f"#<b>{day[i - 1]}</b> - {hm.homework}(Добавлено {hm.upd_date})")
    text = '\n'.join(homework)
    return json_response({'ok': True, 'hw': text})


async def getdb_kab_rasp(request: Request):
    full = request.query
    try:
        uusr = full['user']
    except KeyError:
        uusr = full['_auth'].split('&')[1].split('=')[1]
    d = uusr.replace("'", "\"")
    uusr = json.loads(d)
    try:
        usr = get_student_by_telegram_id(int(uusr['id']))
        if usr is None:
            return json_response({"ok": False, "err": "Unauthorized"}, status=401)
    except ValueError:
        return json_response({"ok": False, "err": "Unauthorized"}, status=401)

    value = []
    for i in range(1, 6):
        value.append('#\n'.join(ast.literal_eval(get_kab_schedule(int(full['kab']), i))))
    val = f"#<b>Понедельник:</b>\n#{value[0]}\n\n#<b>Вторник:</b>\n#{value[1]}" \
          f"\n\n#<b>Среда:</b>\n#{value[2]}\n\n#<b>Четверг:</b>\n#{value[3]}" \
          f"\n\n#<b>Пятница:</b>\n#{value[4]}"
    return json_response({'ok': True, 'rasp': val})


async def getdb_count(request: Request):
    full = request.query
    try:
        uusr = full['user']
    except KeyError:
        uusr = full['_auth'].split('&')[1].split('=')[1]
    d = uusr.replace("'", "\"")
    uusr = json.loads(d)
    try:
        usr = get_student_by_telegram_id(int(uusr['id']))
        if usr is None:
            return json_response({"ok": False, "err": "Unauthorized"}, status=401)
    except ValueError:
        return json_response({"ok": False, "err": "Unauthorized"}, status=401)

    col = get_count()
    return json_response({'ok': True, 'count': col})


async def getdb_comments(request: Request):
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
    cid = data['hash_id']
    cid = cid.split('a')
    d = datetime.date(int(cid[0]), int(cid[1]), int(cid[2]))
    child = int(cid[5]) if cid[5] else None
    try:
        await ns.login(usr.login, usr.password, 1)
        diary = await ns.diary(start=d, student_id=child)
        await ns.logout()
        await ns.logout()
        await ns.logout()
        day = next((item for item in diary.schedule if item.day == d), None)
    except SchoolNotFoundError or AuthError:
        await ns.logout()
        await state.clear()
        await call.message.answer("Неверный логин/пароль.")
        return json_response({"ok": False, "err": "Internal Server Error"}, status=500)
    except NoResponseFromServer:
        return json_response({"ok": False, "err": "Сервер электронного журнала не отвечает"}, status=504)
    lesson = day.lessons[int(cid[3])]
    assignment = lesson.assignments[int(cid[4])]
    asss = assignment.to_json()
    return json_response({'ok': True, 'assignment': asss})

