import os
from dotenv import load_dotenv
from json import JSONEncoder
from aiogram.fsm.state import State, StatesGroup
from aiogram import Bot
from netschoolapi import NetSchoolAPI

from db import Student

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


async def send_duty(student: Student):
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
        await bot.send_message(student.id, f"Вот ваши долги на данное время:\n\n{text}")
    else:
        await bot.send_message(student.id, "На данный момент просроченных заданий нет!")
    await ns.logout()
    await ns.logout()


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
