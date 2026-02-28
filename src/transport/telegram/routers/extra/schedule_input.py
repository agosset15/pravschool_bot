from typing import cast

from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, ShowMode, StartMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Start, SwitchInlineQueryCurrentChat
from aiogram_dialog.widgets.text import Const
from dishka.integrations.aiogram_dialog import FromDishka, inject
from magic_filter import F

from src.core.constants import USER_KEY
from src.core.dto import MessagePayloadDto, UserDto
from src.core.enums import InlineQueryText
from src.services.notification import NotificationService
from src.services.schedule import ScheduleService
from src.services.user import UserService
from src.transport.telegram.states import MainMenu, Register
from src.transport.telegram.utils import I18nFormat
from src.transport.telegram.window import Window


@inject
async def on_schedule_input(
        message: Message,
        widget: MessageInput,
        dialog_manager: DialogManager,
        user_service: FromDishka[UserService],
        schedule_service: FromDishka[ScheduleService],
        notification_service: FromDishka[NotificationService],
) -> None:
    user: UserDto = dialog_manager.middleware_data[USER_KEY]

    text = cast(str, message.text)
    schedule_id = None

    not_found_payload = MessagePayloadDto(
        i18n_key="ntf-schedule.not-found",
        disable_default_markup=False,
    )

    if text.startswith(InlineQueryText.GRADES + "_"):
        id_part = text.removeprefix(InlineQueryText.GRADES + "_")
    elif text.startswith(InlineQueryText.TEACHERS + "_"):
        id_part = text.removeprefix(InlineQueryText.TEACHERS + "_")
    else:
        await notification_service.notify_user(user, not_found_payload)
        return

    try:
        schedule_id = int(id_part)
    except ValueError:
        await notification_service.notify_user(user, not_found_payload)
        return

    schedule = await schedule_service.get(schedule_id)
    if not schedule:
        await notification_service.notify_user(user, not_found_payload)
        return

    await user_service.set_schedule(user, schedule.id)
    await dialog_manager.start(
        state=MainMenu.MAIN,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.DELETE_AND_SEND,
    )

register_grade = Window(
    I18nFormat("msg-register-grade"),
    SwitchInlineQueryCurrentChat(
        I18nFormat("btn-register-grade.grades"),
        Const(InlineQueryText.GRADES),
        id="grades"
    ),
    SwitchInlineQueryCurrentChat(
        I18nFormat("btn-register-grade.teachers"),
        Const(InlineQueryText.TEACHERS),
        id="teachers"
    ),
    Start(
        I18nFormat("btn-back.common"),
        "back",
        state=MainMenu.MAIN,
        show_mode=ShowMode.EDIT,
        mode=StartMode.RESET_STACK
    ),
    MessageInput(func=on_schedule_input, filter=F.text.startswith(InlineQueryText.GRADES)),
    MessageInput(func=on_schedule_input, filter=F.text.startswith(InlineQueryText.TEACHERS)),
    state=Register.GRADE
)

router = Dialog(register_grade)
