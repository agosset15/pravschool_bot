import os
import ast
from datetime import datetime, timedelta
from dotenv import load_dotenv
from json import JSONEncoder
from aiogram.fsm.state import State, StatesGroup
from aiogram import Bot, html
from netschoolapi import NetSchoolAPI
from netschoolapi.errors import SchoolNotFoundError, AuthError

from db import Student
from db.methods.get import get_schedule


ns = NetSchoolAPI('http://d.pravschool.ru/')


class MyEncoder(JSONEncoder):
    def default(self, o):
        thedict = o.__dict__
        thekey = '_sa_instance_state'
        if thekey in thedict: del thedict[thekey]
        return thedict


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
bot = Bot(token=os.getenv('BOT_TOKEN'))


async def id_ad(a):
    with open('ids.txt', 'w+', encoding='utf-8') as ids:
        ids.write(f"{a}")


async def get_duty(student: Student) -> str:
    await ns.login(student.login, student.password, 'Свято-Димитриевская школа')
    ass = await ns.overdue()
    await ns.logout()
    await ns.logout()
    await ns.logout()
    if ass is not None:
        arr = []
        for i in ass:
            date = i.deadline
            await ns.login(student.login, student.password, 'Свято-Димитриевская школа')
            diary = await ns.diary(start=date)
            await ns.logout()
            await ns.logout()
            await ns.logout()
            day = diary.schedule[0]
            lesson = day.lessons
            for less in lesson:
                assig = less.assignments
                if assig:
                    for qw in assig:
                        if qw.id == i.id:
                            arr.append(f'Долг -- {qw.type} по предмету {less.subject}:\n{qw.content}')
        text = "\n\n".join(arr)
        text = f"Вот ваши долги на данное время:\n\n{text}"
    else:
        text = "На данный момент просроченных заданий нет!"
    return text


async def send_duty(student: Student):
    await bot.send_message(student.id, await get_duty(student))


async def send_greeting(student: Student, text: str, morning: bool = False):
    if morning:
        mor = "сегодня"
    else:
        mor = "завтра"
    dt = datetime.now()
    day = dt.weekday()
    if day < 6:
        value = get_schedule(student.clas, day)
        sched = '\n'.join(ast.literal_eval(value))
    else:
        sched = f"{mor} выходной!"
    text += f"Уроки {mor}:\n{sched}"
    await bot.send_message(student.id, text)
    if student.isNs == 1:
        dt = datetime.now()
        start = dt - timedelta(days=dt.weekday())
        try:
            await ns.login(student.login, student.password, 'Свято-Димитриевская школа')
            diary = await ns.diary(start=start)
            await ns.logout()
            await ns.logout()
            await ns.logout()
            day = diary.schedule[dt.weekday()-1]
        except SchoolNotFoundError or AuthError:
            await ns.logout()
            await bot.send_message(student.id, "Неверный логин/пароль от ЭЖ.")
            return
        lesson = day.lessons
        message_text = []
        for less in lesson:
            assig = less.assignments
            if assig:
                for i in assig:
                    if i.mark is None:
                        if i.is_duty is True:
                            message_text.append(
                                f"⚠️ДОЛГ!\n{html.bold(i.type)}({less.subject})\n{i.content}")
                        else:
                            message_text.append(f"{html.bold(i.type)}({less.subject})\n{i.content}")
                    else:
                        message_text.append(
                            f"{html.bold(i.type)}({less.subject})\n{i.content} -- {html.bold(i.mark)}")
            else:
                message_text.append(f"{html.bold(less.subject)}\nЗаданий нет.")
        text = "\n\n".join(message_text)
        msg = f"По версии ЭЖ {mor}:\n\n" + text
        if len(msg) > 4096:
            for x in range(0, len(msg), 4096):
                await bot.send_message(student.id, msg[x:x + 4096], parse_mode='HTML')
        else:
            await bot.send_message(student.id, msg, parse_mode='HTML')
    else:
        await bot.send_message(student.id,"⚠️Вы не ввели свои данные. Введите их в меню настроек.")
    await bot.send_message(student.id, f"{get_duty(student)}")


# ```````````````````````````````````````````````STATES`````````````````````````````````````````````````````````

class Edit(StatesGroup):
    eday = State()
    etext = State()


class Admad(StatesGroup):
    ad = State()


class ClassWait(StatesGroup):
    clas = State()
    uch = State()
    chat_clas = State()


class KabWait(StatesGroup):
    kab = State()


class PaswdWait(StatesGroup):
    password = State()


class ExelWait(StatesGroup):
    file = State()
    rasp = State()
    tchr = State()
    kabs = State()


class AdminAdd(StatesGroup):
    id = State()
    name = State()
    uname = State()
    paswd = State()


class PhotoAdd(StatesGroup):
    kabs = State()
    tchrs = State()
    year = State()


class DelUser(StatesGroup):
    id = State()


class AddNS(StatesGroup):
    login = State()
    password = State()


class GetNS(StatesGroup):
    day = State()


class EditHomework(StatesGroup):
    lesson = State()
    homework = State()
    image = State()


class GetFreeKabs(StatesGroup):
    day = State()
