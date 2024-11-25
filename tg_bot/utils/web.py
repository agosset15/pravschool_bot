from aiohttp.web_request import Request
from aiohttp.web import HTTPUnauthorized, HTTPFound, HTTPExpectationFailed, HTTPGatewayTimeout
from multidict import MultiDictProxy
from aiogram import Bot
from aiogram.utils.web_app import check_webapp_signature, safe_parse_webapp_init_data

from tg_bot.models import DefaultService, User
from tg_bot.utils.ns import update_ns_object, encode_ns_password, get_ns_object, AuthError, NoResponseFromServer
from tg_bot.config import ADMIN_ID


async def validate_request(request: Request, register: bool = False) -> tuple[User, DefaultService]:
    bot: Bot = request.app["bot"]
    db: DefaultService = request.app['db']
    data = request.query if request.method == 'GET' else await request.post()
    if 'tgid' in data.keys() and data['tgid'] == ADMIN_ID:
        user = await db.get_one(User, User.chat_id == ADMIN_ID)
        return user, db
    if not (check_webapp_signature(bot.token, data["_auth"])):
        raise HTTPUnauthorized(reason="WebApp data invalid")
    try:
        web_app_init_data = safe_parse_webapp_init_data(token=bot.token, init_data=data["_auth"])
    except ValueError:
        raise HTTPUnauthorized(reason="WebApp data invalid")
    user = await db.get_one(User, User.chat_id == web_app_init_data.user.id)
    if register:
        if user is None:
            user = await db.create(User, chat_id=web_app_init_data.user.id,
                                   name=web_app_init_data.user.first_name + ' ' + web_app_init_data.user.last_name,
                                   username=web_app_init_data.user.username, ref='WebApp')
        return user, db
    if user is None:
        raise HTTPFound('/register', reason='Not registered')
    return user, db


async def edit_ns_credentials(data: MultiDictProxy, user: User | int, db: DefaultService):
    try:
        ns = await get_ns_object(user)
        encoded_password = await encode_ns_password(ns, data['ns_uname'], data['password'])
        await update_ns_object(user, ns)
    except AuthError as e:
        raise HTTPExpectationFailed(reason=' '.join(e.__notes__))
    except NoResponseFromServer:
        raise HTTPGatewayTimeout(reason="Сервер электронного журнала не отвечает")
    user_id = user.id if isinstance(user, User) else user
    await db.update(User, User.id == user_id, login=data['login'], password=encoded_password, isNs=True)
    if len(ns.students) > 1:
        await db.update(User, User.id == user_id, isParent=True)
