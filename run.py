import asyncio
from aiogram import Bot, Dispatcher
from handlers import common, states, callback, text, inline
from pydantic import BaseSettings, SecretStr


class Settings(BaseSettings):
    bot_token: SecretStr

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


config = Settings()
bot = Bot(token=config.bot_token.get_secret_value())


async def bot_send_message(chat_id, message_text):
    await bot.send_message(chat_id=chat_id, text=message_text)


async def main():
    dp = Dispatcher()

    dp.include_router(common.router)
    dp.include_router(states.router)
    dp.include_router(callback.router)
    dp.include_router(text.router)
    dp.include_router(inline.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
