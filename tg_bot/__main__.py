import logging
import os

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiohttp.web import run_app
from aiohttp.web_app import Application

from aiogram import Dispatcher
from aiogram.webhook.aiohttp_server import setup_application, SimpleRequestHandler

from db import register_models
from .config import bot
from .handlers import common, states, callback, text, inline
from .backend.notifications import send_user_ns_duty
from .web_routes import (add_db_homework, demo_handler, check_data_handler, send_message_handler, getdb_user,
                         getdb_rasp,
                         getdb_kab_rasp,
                         getdb_homework,
                         getdb_count,
                         edit_db_class,
                         edit_db_ns)

WEBHOOK_HOST = 'https://tg.ag15.ru'
WEBHOOK_PATH = '/webhook/pravschool'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

WEBAPP_HOST = 'localhost'
WEBAPP_PORT = 8081


async def on_startup(dispatcher):
    print('Запускаю бота...')
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(WEBHOOK_URL)


def main():
    dp = Dispatcher()
    dp.startup.register(on_startup)
    app = Application()
    app["bot"] = bot

    app.router.add_get("/demo", demo_handler)
    app.router.add_post("/demo/checkData", check_data_handler)
    app.router.add_post("/demo/sendMessage", send_message_handler)
    app.router.add_get("/demo/getDb/homework", getdb_homework)
    app.router.add_get("/demo/getDb", getdb_user)
    app.router.add_get("/demo/getDb/rasp", getdb_rasp)
    app.router.add_get("/demo/getDb/rasp/kab", getdb_kab_rasp)
    app.router.add_post("/demo/editDb/homework", add_db_homework)
    app.router.add_post('/demo/editDb/ns', edit_db_ns)
    app.router.add_post('/demo/editDb/class', edit_db_class)
    app.router.add_get("/demo/getDb/count", getdb_count)

    scheduler = AsyncIOScheduler()

    print('Регаю хендлеры...')
    dp.include_router(common.router)
    dp.include_router(states.router)
    dp.include_router(callback.router)
    dp.include_router(text.router)
    dp.include_router(inline.router)

    print('Запускаю БД...')
    register_models()
    print('Запускаю шедулер...')
    scheduler.start()
    scheduler.add_job(send_user_ns_duty, 'cron', hour=12)
    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    ).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    print('Запускаю ВебСервер...')
    run_app(app, host="127.0.0.1", port=8081)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    os.environ["TZ"] = "Europe/Moscow"
    main()
