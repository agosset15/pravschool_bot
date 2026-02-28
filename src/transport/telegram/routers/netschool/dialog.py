from operator import itemgetter

from aiogram_dialog import Dialog, ShowMode, StartMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import (
    Back,
    Button,
    Group,
    Row,
    Select,
    Start,
    WebApp,
)
from aiogram_dialog.widgets.text import Format
from magic_filter import F

from src.transport.telegram.routers.menu.handlers import on_day_request
from src.transport.telegram.states import MainMenu, NetSchool, NSCredentials
from src.transport.telegram.utils import I18nFormat, IgnoreUpdate
from src.transport.telegram.window import Window

from .getters import ns_day_getter, ns_menu_getter
from .handlers import on_change_week, on_ns_change_student, on_ns_day_selected

menu = Window(
    I18nFormat("msg-netschool-menu"),
    Group(
        WebApp(
            I18nFormat("btn-ns-week.webapp"),
            Format("{mini_app_url}"),
            id="webapp"
        ),
        Select(
            Format("{item[name]}"),
            id="day",
            type_factory=int,
            item_id_getter=itemgetter(0),
            items="days",
            on_click=on_ns_day_selected
        ),
        Row(
            Button(
                I18nFormat("btn-ns-week.prev"),
                "prev_week",
                on_click=on_change_week
            ),
            Start(
                I18nFormat("btn-back.common"),
                "back",
                state=MainMenu.MAIN,
                show_mode=ShowMode.EDIT,
                mode=StartMode.RESET_STACK
            ),
            Button(
                I18nFormat("btn-ns-week.next"),
                "next_week",
                on_click=on_change_week
            ),
        ),
        when=F["is_ns"]
    ),
    Start(
        I18nFormat("btn-goto.ns-credentials"),
        id=NSCredentials.LOGIN.state,
        state=NSCredentials.LOGIN,
        mode=StartMode.RESET_STACK,
        when=~F["is_ns"]
    ),
    MessageInput(func=on_day_request),
    IgnoreUpdate(),
    state=NetSchool.MAIN,
    getter=ns_menu_getter,
)

day = Window(
    I18nFormat("msg-netschool-day"),
    Select(
        I18nFormat(
            "ns-student-select",
            name=F["item"].name,
            is_checked=F["item"].id.is_(F["student_id"])
        ),
        id="student",
        type_factory=int,
        item_id_getter=lambda s: s.id,
        items="children",
        on_click=on_ns_change_student,
        when=F["children"]
    ),
    Back(I18nFormat("btn-back.common")),
    state=NetSchool.DAY,
    getter=ns_day_getter,
)

router = Dialog(
    menu,
)
