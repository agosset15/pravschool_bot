import logging
import asyncio
import sys
from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery

from tg_bot.config import BOT_TOKEN

router = Dispatcher()


@router.message()
async def echo(message: Message):
    await message.answer("Бот находится в режиме обновления. Подождите немного.")


@router.callback_query()
async def call_cho(call: CallbackQuery):
    await call.answer("Бот находится в режиме обновления. Подождите немного.", show_alert=True)


async def main() -> None:
    bot = Bot(token=BOT_TOKEN)

    # And the run events dispatching
    await bot.delete_webhook(drop_pending_updates=False)
    await router.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
