from aiogram.fsm.state import State, StatesGroup


class GradeWait(StatesGroup):
    grade = State()


class RoomWait(StatesGroup):
    room = State()


class PasswordWait(StatesGroup):
    password = State()


class NSLoginCredentialsWait(StatesGroup):
    login = State()
    password = State()


class GetNS(StatesGroup):
    day = State()


class NSChild(StatesGroup):
    duty = State()
    day = State()


class GetFreeRooms(StatesGroup):
    day = State()
