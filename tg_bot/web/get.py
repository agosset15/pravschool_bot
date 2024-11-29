from datetime import date, datetime, timedelta
import random
import json

from aiogram import html
from aiohttp.web import HTTPUnauthorized, HTTPExpectationFailed, HTTPGatewayTimeout, Application
from aiohttp.web_request import Request
from aiohttp.web_response import json_response

from tg_bot.utils.ns import AuthError, NoResponseFromServer, get_ns_object
from tg_bot.utils.web import validate_request
from tg_bot.models import DefaultService, Schedule, User, Day
from tg_bot.config import days


async def getdb_user(request: Request):
    user, db = await validate_request(request)
    password = html.italic("Сохранен в зашифрованном виде")
    ns = await get_ns_object(user)
    return json_response(
        {'ok': True, 'user': {'name': user.name, 'grade': user.grade, 'id': user.id,
                              'is_teacher': user.is_teacher, 'is_ns': user.is_ns,
                              'is_admin': user.is_admin, 'is_parent': user.is_parent, 'pass': password,
                              'login': user.login, 'children': ns.students}})


async def getdb_rasp(request: Request):
    user, db = await validate_request(request)
    day = await db.get_one(Day, Day.id == int(request.match_info['day_id']))
    return json_response({'ok': True, 'schedule': day.text})


async def getdb_homework(request: Request):
    user, db = await validate_request(request)
    day = await db.get_one(Day, Day.id == int(request.match_info['day_id']))
    homework = []
    for lesson in day.lessons:
        if lesson.homework is None:
            homework.append(f"<b>{lesson.name}</b> - Нет<br>")
        else:
            homework.append(f"<b>{lesson.name}</b> - {lesson.homework.homework}(Добавлено {lesson.homework.updated_at})"
                            + f"<a href='#' onclick='send_homework_photo({lesson.homework.id})>Получить фотографию</a>"
                            if lesson.homework.image else '')  # TODO реализовать соответствующую функцию в js
    text = ''.join(homework)
    return json_response({'ok': True, 'hw': text})


async def room_schedule(request: Request):
    user, db = await validate_request(request)
    schedule = await db.get_one(Schedule, Schedule.id == int(request.match_info['kab']))
    values = [f"<b>{day.name}</b>:<br>{day.text}" for day in schedule.days]
    return json_response({'ok': True, 'rasp': '<br><br>'.join(values)})


async def getdb_count(request: Request):
    user, db = await validate_request(request)
    return json_response({'ok': True, 'count': await db.count(User)})


async def getdb_comments(request: Request):
    user, db = await validate_request(request)
    data = [int(x) for x in request.query['hash_id'].split('a')]  # year, month, day, lesson_id, assignment_id

    d = date(data.pop(0), data.pop(0), data.pop(0))
    ns = await get_ns_object(user)
    try:
        diary = await ns.diary(start=d, student_id=int(request.match_info['student_id']))
        lesson = next((item for item in diary.schedule[0].lessons if item.lesson_id == data[0]), None)
        assignment = next((item for item in lesson.assignments if item.id == data[1]), None)
        info = await ns.assignment_info(assignment.id, int(request.match_info['student_id']))
    except AuthError as e:
        raise HTTPExpectationFailed(reason=str(e))
    except NoResponseFromServer:
        raise HTTPGatewayTimeout(reason="Сервер электронного журнала не отвечает")
    return json_response({'ok': True, 'assignment': assignment.json, 'details': info.json})


async def getdb_report(request: Request):
    user, db = await validate_request(request)
    ns = await get_ns_object(user)
    try:
        filters = json.loads(request.query['filters']) if 'filters' in request.query.keys() else None
        report = await ns.report(request.query['uri'], int(request.match_info['student_id']),
                                 filters, requests_timeout=120)
        return json_response({"ok": True, "report": report})
    except AuthError as e:
        raise HTTPExpectationFailed(reason=str(e))
    except NoResponseFromServer:
        raise HTTPGatewayTimeout(reason="Сервер электронного журнала не отвечает")


async def schedule_init(request: Request):
    user, db = await validate_request(request)
    ids = [{'id': day.id, 'name': day.name} for day in (
        await db.get_one(Schedule, Schedule.id == user.schedule)).days]
    return json_response({"ok": True, "days": ids})


async def rooms_init(request: Request):
    user, db = await validate_request(request)
    ids = [{'id': room.id, 'room': room.grade} for room in await db.get_all(Schedule, Schedule.entity == 2)]
    return json_response({"ok": True, "rooms": ids})


async def report_init(request: Request):
    user, db = await validate_request(request)
    ns = await get_ns_object(user)
    response = await ns.init_reports()
    return json_response({"ok": True, "reports": response})


async def getdb_rasp_today(request: Request):
    db: DefaultService = request.app['db']
    user = await db.get_one(User, User.chat_id == int(request.query['tgid']))
    if user is None:
        raise HTTPUnauthorized(reason="Вы не зарегистрированы в боте. Проверьте id на опечатки.")
    now = datetime.now()
    day = "Сегодня"
    weekday = now.weekday()
    if now > datetime(now.year, now.month, now.day) + timedelta(hours=14):
        weekday = (now + timedelta(days=1)).weekday()
        day = "Завтра"
    if weekday > 4:
        return json_response(
            body=str({"ok": True, "rasp": "Выходной!", "tomorrow": f"{day} "
                                                                   f"{(days + ['Суббота', 'Воскресенье'])[weekday]}"}
                     ).encode())
    schedule = await db.get_one(Schedule, Schedule.id == user.schedule)
    return json_response(body=str({"ok": True, "rasp": schedule.days[weekday].text, "tomorrow": f"{day} "
                                                                                                f"{(days + ['Суббота', 'Воскресенье'])[weekday]}"}
                                  ).encode())


async def getdb_rasp_random(request: Request):
    db: DefaultService = request.app['db']
    user = await db.get_one(User, User.chat_id == int(request.query['tgid']))
    if user is None:
        raise HTTPUnauthorized(reason="Вы не зарегистрированы в боте. Проверьте id на опечатки.")
    weekday = random.randint(0, 6)
    day = random.choice(["Завтра", "Сегодня"])
    if weekday > 5:
        return json_response(
            body=str({"ok": True, "rasp": "Выходной!", "tomorrow": f"{day} "
                                                                   f"{(days + ['Суббота', 'Воскресенье'])[weekday]}(ТЕСТ)"}
                     ).encode())
    schedule = await db.get_one(Schedule, Schedule.id == user.schedule)
    return json_response(body=str({"ok": True, "rasp": schedule.days[weekday].text, "tomorrow": f"{day} "
                                                                                                f"{(days + ['Суббота', 'Воскресенье'])[weekday]}(ТЕСТ)"}
                                  ).encode())


async def get_weekdays(request: Request):
    await validate_request(request)
    now = datetime.now()
    year = now.year if now.month >= 9 else now.year - 1
    mon = date(year=year, month=9, day=1)
    if mon.weekday() != 0:
        mon = mon - timedelta(days=mon.weekday())
    sun = mon + timedelta(days=6)
    weeks = [[mon.strftime("%Y-%m-%d"), sun.strftime("%Y-%m-%d")]]
    start = mon
    while True:
        mon = mon + timedelta(weeks=1)
        sun = sun + timedelta(weeks=1)
        weeks.append([mon.strftime("%Y-%m-%d"), sun.strftime("%Y-%m-%d")])
        if sun >= date(start.year + 1, (start - timedelta(days=1)).month, (start - timedelta(days=1)).day):
            break
    if now.weekday() != 0:
        now = now - timedelta(days=now.weekday())
    end = now + timedelta(days=6)
    return json_response({'ok': True, 'weeks': weeks, 'start': now, 'end': end})


async def get_diary(request: Request):
    user, db = await validate_request(request)
    ns = await get_ns_object(user)
    try:
        diary = await ns.diary(datetime.strptime(request.query[['start']], "%Y-%m-%d"),
                               datetime.strptime(request.query[['end']], "%Y-%m-%d"),
                               student_id=int(request.match_info['student_id']))
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
                                                if isinstance(v3, date):
                                                    diary[k][k1][k2].update({k3: v3.strftime('%Ya%ma%d')})
                                    if isinstance(v2, date):
                                        diary[k][k1].update({k2: v2.strftime('%Ya%ma%d')})
                        if isinstance(v1, date):
                            diary[k].update({k1: v1.strftime('%Ya%ma%d')})
            if isinstance(v, date):
                diary.update({k: v.strftime('%Ya%ma%d')})
        return json_response({"ok": True, "dairy": diary})
    except AuthError as e:
        raise HTTPExpectationFailed(reason=str(e))
    except NoResponseFromServer:
        raise HTTPGatewayTimeout(reason="Сервер электронного журнала не отвечает")


def register(app: Application):
    app.router.add_get("/user", getdb_user)
    app.router.add_get("/user/count", getdb_count)

    app.router.add_get("/schedule/{day_id}", getdb_rasp)
    app.router.add_get("/schedule", getdb_rasp_today)
    app.router.add_get("/schedule/init", schedule_init)
    app.router.add_get("/schedule/room/init", rooms_init)
    app.router.add_get("/schedule/room/{room_id}", room_schedule)

    app.router.add_get("/homework/{day_id}", getdb_homework)

    app.router.add_get("/ns/report/{student_id}", getdb_report)
    app.router.add_get("/ns/report/init", report_init)
    app.router.add_get("/ns/comment/{student_id}", getdb_comments)
    app.router.add_get('/ns/weeks', get_weekdays)
    app.router.add_get('/ns/dairy/{student_id}', get_diary)

    app.router.add_get("/test", getdb_rasp_random)
