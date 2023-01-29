import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiogram import Dispatcher
from db import register_models
from .config import bot
from .handlers import common, states, callback, text, inline
from .web_edit.send_duty import send_user_ns_duty



async def main():
    dp = Dispatcher()
    scheduler = AsyncIOScheduler()

    dp.include_router(common.router)
    dp.include_router(states.router)
    dp.include_router(callback.router)
    dp.include_router(text.router)
    dp.include_router(inline.router)

    await bot.delete_webhook(drop_pending_updates=True)
    print('Запускаю БД...')
    register_models()
    print('Запускаю шедулер...')
    scheduler.start()
    scheduler.add_job(send_user_ns_duty, 'cron', hour=12)
    print('Запускаю бота...')
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
