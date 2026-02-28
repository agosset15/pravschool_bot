from typing import cast

from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, ShowMode, StartMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Back, Start
from dishka.integrations.aiogram_dialog import FromDishka, inject
from magic_filter import F

from src.core.constants import USER_KEY
from src.core.dto import MessagePayloadDto, UserDto
from src.services.netschool import NetSchoolService
from src.services.notification import NotificationService
from src.transport.telegram.states import MainMenu, NSCredentials
from src.transport.telegram.utils import I18nFormat
from src.transport.telegram.window import Window


@inject
async def on_login_input(
        message: Message,
        widget: MessageInput,
        dialog_manager: DialogManager,
) -> None:
    text = cast(str, message.text)
    dialog_manager.dialog_data["login"] = text

    await message.delete()
    await dialog_manager.switch_to(
        state=NSCredentials.PASSWORD,
        show_mode=ShowMode.EDIT,
    )


@inject
async def on_password_input(
        message: Message,
        widget: MessageInput,
        dialog_manager: DialogManager,
        netschool_service: FromDishka[NetSchoolService],
        notification_service: FromDishka[NotificationService]
) -> None:
    user: UserDto = dialog_manager.middleware_data[USER_KEY]
    raw_password = cast(str, message.text)
    login = dialog_manager.dialog_data["login"]
    await message.delete()

    user.login = login
    success = await netschool_service.register(user, raw_password)

    if not success:
        await notification_service.notify_user(user, MessagePayloadDto(
            i18n_key="ntf-error.incorrect-credentials",
            disable_default_markup=False,
        ))
        await dialog_manager.start(
            state=NSCredentials.LOGIN,
            show_mode=ShowMode.EDIT,
            mode=StartMode.RESET_STACK
        )
        return

    await dialog_manager.start(
        state=MainMenu.MAIN,
        show_mode=ShowMode.EDIT,
        mode=StartMode.RESET_STACK
    )


register_netschool_login = Window(
    I18nFormat("msg-ns-credentials.login"),
    Start(
        I18nFormat("btn-back.close"),
        "back",
        state=MainMenu.MAIN,
        show_mode=ShowMode.EDIT,
        mode=StartMode.RESET_STACK
    ),
    MessageInput(func=on_login_input, filter=F.text),
    state=NSCredentials.LOGIN
)

register_netschool_password = Window(
    I18nFormat("msg-ns-credentials.password"),
    Back(
        I18nFormat("btn-back.common"),
        "back",
        show_mode=ShowMode.EDIT,
    ),
    MessageInput(func=on_login_input, filter=F.text),
    state=NSCredentials.LOGIN
)

router = Dialog(register_netschool_login)
