from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from sys import exit


bot_token = "5399460388:AAGde_VkV6OgBt5BW1GSoUvck4sPxQjfR9U"
if not bot_token:
    exit("Error: no token provided")

bot = Bot(token=bot_token)

dp = Dispatcher(bot, storage=MemoryStorage())

