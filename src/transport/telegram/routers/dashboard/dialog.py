from aiogram_dialog import Dialog
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Start, SwitchTo
from magic_filter import F

from src.transport.telegram.states import AdminDashboard, MainMenu
from src.transport.telegram.utils import I18nFormat, IgnoreUpdate
from src.transport.telegram.window import Window

from .handlers import on_add_photo, on_add_schedule

dashboard = Window(
    I18nFormat("msg-dashboard"),
    SwitchTo(
        I18nFormat("btn-admin.schedule"),
        id="new_rasp",
        state=AdminDashboard.SCHEDULE
    ),
    SwitchTo(
        I18nFormat("btn-admin.photo"),
        id="photo_add",
        state=AdminDashboard.ADD_YEAR_PHOTO
    ),
    Button(I18nFormat("btn-admin.users"), id="users_check"),
    Button(I18nFormat("btn-admin.broadcast"), id="ad"),
    Start(
        I18nFormat("btn-back.common"),
        id="back",
        state=MainMenu.MAIN
    ),
    IgnoreUpdate(),
    state=AdminDashboard.MAIN
)

add_schedule = Window(
    I18nFormat("msg-add-schedule"),
    SwitchTo(
        I18nFormat("btn-back.common"),
        id="back",
        state=AdminDashboard.MAIN
    ),
    MessageInput(func=on_add_schedule, filter=F.document),
    IgnoreUpdate(),
    state=AdminDashboard.SCHEDULE
)

add_photo = Window(
    I18nFormat("msg-add-photo"),
    SwitchTo(
        I18nFormat("btn-back.common"),
        id="back",
        state=AdminDashboard.MAIN
    ),
    MessageInput(func=on_add_photo, filter=F.photo),
    IgnoreUpdate(),
    state=AdminDashboard.ADD_YEAR_PHOTO
)

router = Dialog(
    dashboard,
    add_schedule,
    add_photo
)
