from aiohttp.web import HTTPExpectationFailed, HTTPGatewayTimeout, HTTPNotAcceptable, Application
from aiohttp.web_request import Request
from aiohttp.web_response import json_response

from aiogram import Bot, html
from aiogram.types import BufferedInputFile

from tg_bot.models import User, Schedule
from tg_bot.utils.ns import AuthError, NoResponseFromServer, get_ns_object
from tg_bot.utils.web import validate_request, edit_ns_credentials


async def get_attachment_file(request: Request):
    bot: Bot = request.app['bot']
    user, db = await validate_request(request)
    data = await request.post()
    ns = await get_ns_object(user)
    try:
        file = await ns.download_attachment(int(data['attachment_id']), int(data['assignment_id']),
                                            int(data['student_id']))
        info = await ns.assignment_info(int(data['assignment_id']), int(data['student_id']))
        name = (next((attachment for attachment in info.attachments if attachment.id == int(data['attachment_id'])),
                     None)).name
    except AuthError as e:
        raise HTTPExpectationFailed(reason=' '.join(e.__notes__))
    except NoResponseFromServer:
        raise HTTPGatewayTimeout(reason="Сервер электронного журнала не отвечает")
    await bot.send_document(user.chat_id, BufferedInputFile(file, name),
                            caption=f"{html.bold(info.subject.name)}\n{info.name}", parse_mode='HTML')
    return json_response({"ok": True})


async def edit_db_class(request: Request):
    user, db = await validate_request(request)
    data = await request.post()
    await db.update(User, User.id == user.id, grade=data['grade'])
    return json_response({"ok": True})


async def edit_db_ns(request: Request):
    user, db = await validate_request(request)
    data = await request.post()
    await edit_ns_credentials(data, user, db)
    return json_response({'ok': True})


async def register_user(request: Request):
    user, db = await validate_request(request, True)
    if not isinstance(user, int):
        raise HTTPNotAcceptable(reason="Authorized")
    data = await request.post()
    await edit_ns_credentials(data, user, db)
    schedule = await db.get_one(Schedule, Schedule.grade == data['grade'],
                                Schedule.entity == int(data['is_tchr'] == 'true'))
    await db.update(User, User.id == user, grade=data['grade'], isTeacher=(data['is_teacher'] == 'true'),
                    duty_notification=(data['is_notifications'] == 'true'), schedule=schedule.id)
    return json_response({'ok': True})


def register(app: Application):
    app.router.add_post('/user/register', register_user)
    app.router.add_post('/user/edit/ns', edit_db_ns)
    app.router.add_post('/user/edit/grade', edit_db_class)

    app.router.add_post("/ns/send_attachment", get_attachment_file)
