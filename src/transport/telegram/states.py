from typing import Optional

from aiogram.fsm.state import State, StatesGroup


class MainMenu(StatesGroup):
    MAIN = State()
    ROOMS = State()
    ROOMS_FREE = State()
    SETTINGS = State()


class Notification(StatesGroup):
    CLOSE = State()


class NetSchool(StatesGroup):
    MAIN = State()
    DAY = State()
    CHOOSE_CHILD = State()


class Register(StatesGroup):
    GRADE = State()


class NSCredentials(StatesGroup):
    LOGIN = State()
    PASSWORD = State()


class AdminDashboard(StatesGroup):
    MAIN = State()
    SCHEDULE = State()
    ADD_YEAR_PHOTO = State()

class DashboardUser(StatesGroup):
    MAIN = State()


class Homework(StatesGroup):
    MAIN = State()

##############
class Advert(StatesGroup):
    TEXT = State()


class EditHomework(StatesGroup):
    LESSON = State()
    HOMEWORK = State()
    IMAGE = State()


def state_from_string(state_str: str, sep: Optional[str] = ":") -> Optional[State]:
    """Convert a state string (e.g., 'MainMenu:MAIN') to a State object."""
    try:
        group_name, state_name = state_str.split(sep)[:2]
        group_cls = globals().get(group_name)
        if group_cls is None:
            return None
        state_obj = getattr(group_cls, state_name, None)
        if not isinstance(state_obj, State):
            return None
        return state_obj
    except (ValueError, AttributeError):
        return None
