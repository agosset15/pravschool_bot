from aiogram.fsm.state import State, StatesGroup


class Advert(StatesGroup):
    text = State()


class ExcelWait(StatesGroup):
    file = State()
    students = State()
    teachers = State()
    rooms = State()


class PhotoAdd(StatesGroup):
    year = State()


class EditHomework(StatesGroup):
    lesson = State()
    homework = State()
    image = State()
