from json import JSONEncoder
from aiogram.fsm.state import State, StatesGroup
from aiogram import Bot
from pydantic import BaseSettings, SecretStr
from netschoolapi import NetSchoolAPI

ns = NetSchoolAPI('http://d.pravschool.ru/')


class Settings(BaseSettings):
    bot_token: SecretStr

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

class MyEncoder(JSONEncoder):
    def default(self, o):
        thedict = o.__dict__
        thekey = '_sa_instance_state'
        if thekey in thedict: del thedict[thekey]
        return thedict


config = Settings()
bot = Bot(token=config.bot_token.get_secret_value())

async def id_ad(a):
    with open('ids.txt', 'w+', encoding='utf-8') as ids:
        ids.write(f"{a}")


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
