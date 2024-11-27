import os
import secrets
from tg_bot.utils.redis import BaseRedis

from pathlib import Path, PurePath
from typing import Final


def get_secret(key, default=None):
    value = os.getenv(key, default=default)
    if os.path.isfile(value):
        with open(value) as f:
            return f.read()
    return value


ROOT_DIR: Final[Path] = Path(__file__).parent.parent
BOT_DIR: Final[PurePath] = PurePath(ROOT_DIR / "tg_bot")

BOT_TOKEN = get_secret("BOT_TOKEN")
DEBUG = os.getenv("DEBUG")
ADMIN_ID = int(os.getenv("ADMIN_ID", default=900645059))

DOMAIN = os.getenv("DOMAIN", default="example.com")
SECRET_KEY = secrets.token_urlsafe(48)
WEBHOOK_BASE_PATH = os.getenv("WEBHOOK_BASE_PATH", default="/webhook")
WEBHOOK_PATH = f"{WEBHOOK_BASE_PATH}/{SECRET_KEY}"
WEBHOOK_URL = f"https://{DOMAIN}{WEBHOOK_PATH}"
WEBAPI_PORT = int(os.getenv("WEBAPI_PORT", default=8080))
WEBAPI_HOST = os.getenv("WEBAPI_HOST", default="localhost")


REDIS_HOST = os.getenv("REDIS_HOST", default="localhost")
REDIS_USERNAME = os.getenv("REDIS_USERNAME", default="default")
REDIS_PORT = os.getenv("REDIS_PORT", default=6379)
REDIS_PASSWORD = get_secret("REDIS_PASSWORD", "nOtSaFePaSsWoRd")
REDIS_DB_FSM = os.getenv("REDIS_DB_FSM", default="0")
REDIS_DB_JOBSTORE = os.getenv("REDIS_DB_JOBSTORE", default="1")
REDIS_DB_CACHE = os.getenv("REDIS_DB_CACHE", default=3)
REDIS_FSM_URI = f"redis://{REDIS_USERNAME}:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB_FSM}"
cache = BaseRedis(REDIS_HOST, REDIS_PASSWORD, REDIS_PORT, REDIS_DB_CACHE, REDIS_USERNAME)

DB_HOST = os.getenv("DB_HOST", default="localhost")
DB_PORT = os.getenv("DB_PORT", default=5432)
DB_PASSWORD = get_secret("DB_PASSWORD", default="")
DB_USER = os.getenv("DB_USER", default="aiogram")
DB_NAME = os.getenv("DB_NAME", default="aiogram")
DB_DRIVER = os.getenv('DB_DRIVER')
DB_URI = f"{DB_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

NS_URL = os.getenv("NS_URL")
LOG_CHAT = os.getenv("LOG_CHAT")

# TODO: избавиться от `grades`
grades = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10и", "10м", "10о", "11о", "11м", "11и"]
days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница"]
times = ['08:40 - 09:25', '09:35 - 10:20', '10:30 - 11:15', '11:25 - 12:10', '12:25 - 13:10', '13:25 - 14:10',
             '14:25 - 15:10', '15:20 - 16:05', '16:15-17:00', 'после 17:00']

# async def send_greeting(user: User, text: str, morning: bool = False):
#     if morning:
#         mor = "сегодня"
#     else:
#         mor = "завтра"
#     dt = datetime.now()
#     day = dt.weekday()
#     if day < 6:
#         value = get_schedule(student.grade, day)
#         sched = '\n'.join(ast.literal_eval(value))
#     else:
#         sched = f"{mor} выходной!"
#     text += f"Уроки {mor}:\n{sched}"
#     await bot.send_message(student.id, text)
#     if student.is_ns == 1:
#         dt = datetime.now()
#         start = dt - timedelta(days=dt.weekday())
#         try:
#             await ns.login(student.login, student.password, 'Свято-Димитриевская школа')
#             diary = await ns.diary(start=start)
#             await ns.logout()
#             await ns.logout()
#             await ns.logout()
#             day = diary.schedule[dt.weekday() - 1]
#         except SchoolNotFoundError or AuthError:
#             await ns.logout()
#             await bot.send_message(student.id, "Неверный логин/пароль от ЭЖ.")
#             return
#         lesson = day.lessons
#         message_text = []
#         for less in lesson:
#             assig = less.assignments
#             if assig:
#                 for i in assig:
#                     if i.mark is None:
#                         if i.is_duty is True:
#                             message_text.append(
#                                 f"⚠️ДОЛГ!\n{html.bold(i.type)}({less.subject})\n{i.content}")
#                         else:
#                             message_text.append(f"{html.bold(i.type)}({less.subject})\n{i.content}")
#                     else:
#                         message_text.append(
#                             f"{html.bold(i.type)}({less.subject})\n{i.content} -- {html.bold(i.mark)}")
#             else:
#                 message_text.append(f"{html.bold(less.subject)}\nЗаданий нет.")
#         text = "\n\n".join(message_text)
#         msg = f"По версии ЭЖ {mor}:\n\n" + text
#         if len(msg) > 4096:
#             for x in range(0, len(msg), 4096):
#                 await bot.send_message(student.id, msg[x:x + 4096], parse_mode='HTML')
#         else:
#             await bot.send_message(student.id, msg, parse_mode='HTML')
#     else:
#         await bot.send_message(student.id, "⚠️Вы не ввели свои данные. Введите их в меню настроек.")
#     # await bot.send_message(student.id, f"{get_duty(student)}")
