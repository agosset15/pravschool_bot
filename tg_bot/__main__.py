import logging
import os

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiohttp.web import run_app, Application

from aiogram import Dispatcher
from aiogram.webhook.aiohttp_server import setup_application, SimpleRequestHandler

from tg_bot.models import db_manager, DefaultService
from tg_bot.misc import bot, storage, ns_sessions
from tg_bot.handlers import common, states, callback, text, inline, service, admin
# from tg_bot.utils.notifications import send_user_ns_duty
from tg_bot.middlewares import DatabaseMiddleware
from tg_bot.web import get, post
from tg_bot.config import WEBHOOK_URL, WEBHOOK_PATH, WEBAPI_PORT, WEBAPI_HOST


class StartUpFactory:
    def __init__(self):
        self.session = None

    async def bot(self, dispatcher: Dispatcher):
        print('Запускаю БД...')
        db = DefaultService(self.session)
        register_global_middlewares(dispatcher, db)
        print('Запускаю бота...')
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.set_webhook(WEBHOOK_URL)

    async def server(self, app):
        print('Запускаю БД...')
        db_manager.init()
        self.session = db_manager.session
        app["db"] = DefaultService(self.session)
        yield
        await db_manager.close()


async def clean_ns_sessions(dispatcher):
    for session in ns_sessions.values():
        await session.full_logout(requests_timeout=120)


def register_global_middlewares(dp: Dispatcher, db):
    dp.message.outer_middleware(DatabaseMiddleware(db))
    dp.callback_query.outer_middleware(DatabaseMiddleware(db))
    dp.inline_query.outer_middleware(DatabaseMiddleware(db))
    dp.my_chat_member.outer_middleware(DatabaseMiddleware(db))


def main():
    startup = StartUpFactory()
    dp = Dispatcher(storage=storage)
    dp.startup.register(startup.bot)
    dp.shutdown.register(clean_ns_sessions)

    app = Application()
    app["bot"] = bot
    app.cleanup_ctx.append(startup.server)
    post.register(app)
    get.register(app)

    scheduler = AsyncIOScheduler()

    print('Регаю хендлеры...')
    dp.include_routers(common.router, states.router, callback.router, text.router, inline.router, admin.router,
                       service.router)

    print('Запускаю шедулер...')
    scheduler.start()
    # scheduler.add_job(send_user_ns_duty, 'cron', hour=12)

    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    ).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    print('Запускаю ВебСервер...')
    run_app(app, host=WEBAPI_HOST, port=WEBAPI_PORT)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    os.environ["TZ"] = "Europe/Moscow"
    main()
