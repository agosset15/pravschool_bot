import ast
import json
import datetime
import random
from pathlib import Path

from aiogram import html
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


async def getdb_user(request: Request):
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

    classs = usr.clas
    class_list = [101, 102, 103, 111, 112, 113]
    list1 = {101: '10г', 102: "10е", 103: '10ф', 111: '11г', 112: '11е', 113: '11ф'}
    if classs in class_list:
        classs = list1[classs]
    paswd = usr.password
    if paswd:
        if paswd[0] == '[':
            paswd = html.italic("Сохранен в зашифрованном виде")
        else:
            paswd = html.italic("Сохранен в незашифрованном виде. Рекомендуется его переписать.")
    if data['children'] == 'true':
        try:
            await ns.login(usr.login, usr.password, 1)
            stt = await ns.students()
            await ns.logout()
            await ns.logout()
            await ns.logout()
            return json_response(
                {'ok': True, 'user': {'name': usr.name, 'clas': classs, 'id': usr.id, 'isTeacher': usr.isTeacher,
                                      'isNs': usr.isNs, 'ntf': usr.duty_notification, 'isAdmin': usr.isAdmin,
                                      'isParent': usr.isParent, 'pass': paswd, 'login': usr.login}, 'children': stt})
        except AuthError:
            await ns.logout()
            await ns.logout()
            return json_response({"ok": False, "err": "Internal Server Error"}, status=500)
        except NoResponseFromServer:
            await ns.logout()
            await ns.logout()
            return json_response({"ok": False, "err": "Сервер электронного журнала не отвечает"}, status=504)
    else:
        return json_response(
            {'ok': True, 'user': {'name': usr.name, 'clas': classs, 'id': usr.id, 'isTeacher': usr.isTeacher,
                                  'isNs': usr.isNs, 'ntf': usr.duty_notification, 'isAdmin': usr.isAdmin,
                                  'isParent': usr.isParent, 'pass': paswd, 'login': usr.login}})


async def getdb_rasp(request: Request):
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
    if usr.isTeacher is True:
        rasp = get_teacher_schedule(usr.clas, int(data['day']))
    else:
        rasp = get_schedule(usr.clas, int(data['day']))
    res = ''.join(ast.literal_eval(rasp))
    return json_response({'ok': True, 'rasp': res})


async def getdb_homework(request: Request):
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

    day = ast.literal_eval(get_schedule(usr.clas, int(data['day'])))
    homework = []
    for i in range(1, len(day) + 1):
        hm = get_homework(i, usr.clas, int(data['day']))
        if hm is None:
            homework.append(f"#<b>{day[i - 1]}</b> - Нет")
        else:
            homework.append(f"#<b>{day[i - 1]}</b> - {hm.homework}(Добавлено {hm.upd_date})")
    text = '\n'.join(homework)
    return json_response({'ok': True, 'hw': text})


async def getdb_kab_rasp(request: Request):
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

    value = []
    for i in range(1, 6):
        value.append('#\n'.join(ast.literal_eval(get_kab_schedule(int(data['kab']), i))))
    val = f"#<b>Понедельник:</b>\n#{value[0]}\n\n#<b>Вторник:</b>\n#{value[1]}" \
          f"\n\n#<b>Среда:</b>\n#{value[2]}\n\n#<b>Четверг:</b>\n#{value[3]}" \
          f"\n\n#<b>Пятница:</b>\n#{value[4]}"
    return json_response({'ok': True, 'rasp': val})


async def getdb_count(request: Request):
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
    try:
        child = int(cid[5])
    except IndexError:
        child = None
    try:
        await ns.login(usr.login, usr.password, 1)
        diary = await ns.diary(start=d, student_id=child)
        lesson = next((item for item in diary.schedule[0].lessons if item.lesson_id == int(cid[3])), None)
        assignment = next((item for item in lesson.assignments if item.id == int(cid[4])), None)
        info = await ns.assignment_info(assignment.id, child)
        await ns.logout()
        await ns.logout()
        await ns.logout()
    except (AuthError, SchoolNotFoundError):
        await ns.logout()
        return json_response({"ok": False, "err": "Internal Server Error"}, status=500)
    except NoResponseFromServer:
        return json_response({"ok": False, "err": "Сервер электронного журнала не отвечает"}, status=504)
    asss = assignment.to_json()
    details = {'id': info.id, 'name': info.name, 'subject': info.subjectGroup.name, 'teachers': [],
               'weight': info.weight, 'description': info.description, 'attachments': []}
    for i in info.teachers:
        details['teachers'].append({'id': i.id, 'name': i.name})
    for i in info.attachments:
        details['attachments'].append({'id': i.id, 'name': i.name, 'description': i.description})
    return json_response({'ok': True, 'assignment': asss, 'details': details, 'child': child})


async def getdb_report(request: Request):
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
        await ns.login(usr.login, usr.password, 1)
        file = await ns.report(data['uri'], data['clid'], data['sid'], requests_timeout=120)
        await ns.logout()
        await ns.logout()
        return json_response({"ok": True, "report": file})
    except AuthError:
        await ns.logout()
        await ns.logout()
        return json_response({"ok": False, "err": "Internal Server Error"}, status=500)
    except NoResponseFromServer:
        await ns.logout()
        await ns.logout()
        return json_response({"ok": False, "err": "Сервер электронного журнала не отвечает"}, status=504)


async def getdb_rasp_today(request: Request):
    data = request.query
    try:
        usr = get_student_by_telegram_id(int(data['tgid']))
        if usr is None:
            return json_response({"ok": False, "err": "Unauthorized"}, status=401)
    except ValueError:
        return json_response({"ok": False, "err": "Unauthorized"}, status=401)
    date = datetime.date.today().weekday() + 1
    tomorrow = datetime.datetime.now() > datetime.datetime(datetime.date.today().year, datetime.date.today().month,
                                                           datetime.date.today().day) + datetime.timedelta(hours=14)
    if tomorrow:
        date = datetime.date.today().weekday() + 2
    tomorrow = {True: "Завтра", False: "Сегодня"}[tomorrow]
    days = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]
    if date > 5:
        if date > 7:
            date = date - 7
        else:
            return json_response(
                body=str({"ok": True, "rasp": "Выходной!", "tomorrow": f"{tomorrow} {days[date - 1]}"}).encode())
    if usr.isTeacher is True:
        rasp = get_teacher_schedule(usr.clas, date)
    else:
        rasp = get_schedule(usr.clas, date)
    res = '\n'.join(ast.literal_eval(rasp))
    return json_response(body=str({"ok": True, "rasp": res, "tomorrow": f"{tomorrow} {days[date - 1]}"}).encode())


async def getdb_rasp_random(request: Request):
    data = request.query
    try:
        usr = get_student_by_telegram_id(int(data['tgid']))
        if usr is None:
            return json_response({"ok": False, "err": "Unauthorized"}, status=401)
    except ValueError:
        return json_response({"ok": False, "err": "Unauthorized"}, status=401)
    date = random.randint(1, 7)
    tomorrow = random.choice(["Завтра", "Сегодня"])
    if date > 5:
        if date > 7:
            date = date - 7
        else:
            return json_response(body=str({"ok": True, "rasp": "Выходной!", "tomorrow": f"{tomorrow}(ТЕСТ)"}).encode())
    if usr.isTeacher is True:
        rasp = get_teacher_schedule(usr.clas, date)
    else:
        rasp = get_schedule(usr.clas, date)
    res = '\n'.join(ast.literal_eval(rasp))
    return json_response(body=str({"ok": True, "rasp": res, "tomorrow": f"{tomorrow}(ТЕСТ)"}).encode())


async def get_weekdays(request: Request):
    year = datetime.date.today().year if datetime.date.today().month >= 9 else datetime.date.today().year - 1
    mon = datetime.date(year=year, month=9, day=1)
    if mon.weekday() != 0:
        mon = mon - datetime.timedelta(days=mon.weekday())
    sun = mon + datetime.timedelta(days=6)
    weeks = [[mon.strftime("%Y-%m-%d"), sun.strftime("%Y-%m-%d")]]
    start = mon
    while True:
        mon = mon + datetime.timedelta(weeks=1)
        sun = sun + datetime.timedelta(weeks=1)
        weeks.append([mon.strftime("%Y-%m-%d"), sun.strftime("%Y-%m-%d")])
        if sun >= datetime.date((start - datetime.timedelta(days=1)).year + 1,
                                (start - datetime.timedelta(days=1)).month, (start - datetime.timedelta(days=1)).day):
            break
    this = datetime.date.today()
    if this.weekday() != 0:
        this = this - datetime.timedelta(days=this.weekday())
    end = this + datetime.timedelta(days=6)
    return json_response({'ok': True, 'weeks': weeks, 'start': this, 'end': end})


async def get_diary(request: Request):
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
        await ns.login(usr.login, usr.password, 1)
        diary = await ns.diary(datetime.datetime.strptime(data[['start']], "%Y-%m-%d"),
                               datetime.datetime.strptime(data[['end']], "%Y-%m-%d"), student_id=data['student'])
        await ns.logout()
        await ns.logout()
        diary = diary.__dict__
        for k, v in diary.items():  # Diary
            if isinstance(v, list):
                for l1 in v:
                    for k1, v1 in l1.items():  # Day
                        if isinstance(v1, list):
                            for l2 in v1:
                                for k2, v2 in l2.items():  # Lesson
                                    if isinstance(v2, list):
                                        for l3 in v2:
                                            for k3, v3 in l3.items():  # Assignment
                                                if isinstance(v3, datetime.date):
                                                    diary[k][k1][k2].update(k3, v3.strftime('%Ya%ma%d'))
                                    if isinstance(v2, datetime.date):
                                        diary[k][k1].update(k2, v2.strftime('%Ya%ma%d'))
                        if isinstance(v1, datetime.date):
                            diary[k].update(k1, v1.strftime('%Ya%ma%d'))
            if isinstance(v, datetime.date):
                diary.update(k, v.strftime('%Ya%ma%d'))
        return json_response({"ok": True, "report": diary})
    except AuthError:
        await ns.logout()
        await ns.logout()
        return json_response({"ok": False, "err": "Internal Server Error"}, status=500)
    except NoResponseFromServer:
        await ns.logout()
        await ns.logout()
        return json_response({"ok": False, "err": "Сервер электронного журнала не отвечает"}, status=504)
