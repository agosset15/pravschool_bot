from operator import itemgetter

from aiogram_dialog import Dialog, ShowMode, StartMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import (
    Button,
    Column,
    Row,
    Select,
    Start,
    SwitchInlineQueryChosenChatButton,
    SwitchInlineQueryCurrentChat,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const, Format
from magic_filter import F

from src.core.enums import InlineQueryText
from src.transport.telegram.states import (
    AdminDashboard,
    MainMenu,
    NetSchool,
    NSCredentials,
    Register,
)
from src.transport.telegram.utils import I18nFormat, IgnoreUpdate
from src.transport.telegram.window import Window

from .getters import bot_info_getter, days_getter, menu_getter
from .handlers import (
    on_become_admin,
    on_day_request,
    on_free_rooms_day_selected,
    on_get_today,
    on_get_tomorrow,
    on_get_week,
    on_get_year,
    on_room_request,
)

menu = Window(
    I18nFormat("msg-main-menu"),
    Row(
        Button(
            text=I18nFormat("btn-menu.today"),
            id="today",
            on_click=on_get_today,
        ),
        Button(
            text=I18nFormat("btn-menu.tomorrow"),
            id="tomorrow",
            on_click=on_get_tomorrow,
        ),
    ),
    Row(
        SwitchTo(
            text=I18nFormat("btn-menu.rooms"),
            id="rooms",
            state=MainMenu.ROOMS
        ),
        Start(
            text=I18nFormat("btn-menu.netschool"),
            id="netschool",
            state=NetSchool.MAIN,
            show_mode=ShowMode.EDIT,
        ),
    ),
    Row(
        Button(
            text=I18nFormat("btn-menu.week"),
            id="week",
            on_click=on_get_week,
        ),
        Button(
            text=I18nFormat("btn-menu.year"),
            id="year",
            on_click=on_get_year,
        ),
    ),
    Row(
        SwitchInlineQueryChosenChatButton(
            text=I18nFormat("btn-menu.inline"),
            query=Const(""),
            allow_channel_chats=True,
            allow_user_chats=True,
            allow_group_chats=True,
            allow_bot_chats=True
        ),
        SwitchTo(
            text=I18nFormat("btn-menu.settings"),
            id="settings",
            state=MainMenu.SETTINGS,
            show_mode=ShowMode.EDIT
        )
    ),
    Row(
        Start(
            text=I18nFormat("btn-menu.admin"),
            id="admin",
            state=AdminDashboard.MAIN,
            when=F["is_dev"]
        )
    ),
    MessageInput(func=on_day_request),
    IgnoreUpdate(),
    state=MainMenu.MAIN,
    getter=menu_getter,
)


rooms = Window(
    I18nFormat("msg-rooms-menu"),
    Row(
        SwitchTo(
            text=I18nFormat("btn-rooms.free"),
            id="free",
            state=MainMenu.ROOMS_FREE,
            show_mode=ShowMode.EDIT,
        ),
    ),
    Row(
        SwitchInlineQueryCurrentChat(
            text=I18nFormat("btn-rooms.find"),
            switch_inline_query_current_chat=Const(InlineQueryText.ROOMS),
        ),
    ),
    SwitchTo(
        I18nFormat("btn-back.common"),
        id="back",
        state=MainMenu.MAIN,
    ),
    MessageInput(func=on_room_request, filter=F.text.startswith(InlineQueryText.ROOMS)),
    IgnoreUpdate(),
    state=MainMenu.ROOMS,
)

rooms_free = Window(
    I18nFormat("msg-rooms.select-day"),
    Select(
        text=Format("{item[1]}"),
        item_id_getter=itemgetter(0),
        id="day_select",
        items="days",
        type_factory=int,
        on_click=on_free_rooms_day_selected
    ),
    Row(
        SwitchTo(
            text=I18nFormat("btn-back.common"),
            id="back",
            state=MainMenu.ROOMS,
        ),
    ),
    state=MainMenu.ROOMS_FREE,
    getter=days_getter
)

settings = Window(
    I18nFormat("msg-settings-menu"),
    Column(
        Start(
            I18nFormat("btn-settings.change-class"),
            id="change_class",
            state=Register.GRADE,
            mode=StartMode.RESET_STACK,
        ),
        Start(
            I18nFormat("btn-settings.ns-credentials"),
            id="ns_credentials",
            state=NSCredentials.LOGIN,
            mode=StartMode.RESET_STACK,
        ),
        # TODO: implement notifications
        # Button(
        #     I18nFormat("btn-settings.notifications"),
        #     id="notifications",
        # ),
        Button(
            I18nFormat("btn-settings.become-admin"),
            id="become_admin",
            on_click=on_become_admin,
        ),
        SwitchTo(
            I18nFormat("btn-back.common"),
            id="back",
            state=MainMenu.MAIN,
        ),
    ),
    state=MainMenu.SETTINGS,
    getter=bot_info_getter
)


router = Dialog(
    menu,
    rooms,
    rooms_free,
    settings,
)
