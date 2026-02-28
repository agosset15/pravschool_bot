from aiogram_dialog import Dialog
from aiogram_dialog.widgets.kbd import Button, Start

from src.transport.telegram.states import AdminDashboard, DashboardUser
from src.transport.telegram.utils import I18nFormat, IgnoreUpdate
from src.transport.telegram.window import Window

dashboard = Window(
    I18nFormat("msg-user-dashboard"),
    Button(I18nFormat("btn-user-dash.admin"), id="toggle_admin"),
    Button(I18nFormat("btn-user-dash.delete"), id="delete"),
    Button(I18nFormat("btn-user-dash.message"), id="ad"),
    Start(
        I18nFormat("btn-back.common"),
        id="back",
        state=AdminDashboard.MAIN
    ),
    IgnoreUpdate(),
    state=DashboardUser.MAIN
)

router = Dialog(
    dashboard
)
