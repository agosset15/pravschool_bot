from datetime import timedelta

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode, StartMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Select
from dishka.integrations.aiogram_dialog import FromDishka, inject
from fluentogram import TranslatorRunner
from loguru import logger

from src.core.config import AppConfig
from src.core.constants import USER_KEY
from src.core.dto import MediaDescriptorDto, MessagePayloadDto, UserDto
from src.core.enums import InlineQueryText, MediaType, UserRole, WeekDay
from src.core.utils import datetime_now
from src.services.notification import NotificationService
from src.services.schedule import ScheduleService
from src.services.schedules_extra import SchedulesExtraService
from src.services.user import UserService
from src.transport.telegram.keyboards import get_register_grade_keyboard, get_time_keyboard
from src.transport.telegram.states import MainMenu

router = Router(name=__name__)


async def on_start_dialog(user: UserDto, dialog_manager: DialogManager) -> None:
    logger.info(f"{user.log} Started dialog")
    await dialog_manager.start(
        state=MainMenu.MAIN,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.DELETE_AND_SEND,
    )


@router.message(CommandStart(ignore_case=True))
async def on_start_command(message: Message, user: UserDto, dialog_manager: DialogManager) -> None:
    await on_start_dialog(user, dialog_manager)


@inject
async def on_get_today(
    callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
    i18n: FromDishka[TranslatorRunner],
    user_service: FromDishka[UserService],
    notification_service: FromDishka[NotificationService],
) -> None:
    user: UserDto = dialog_manager.middleware_data[USER_KEY]
    user_schedule = await user_service.get_schedule(user)

    if not user_schedule:
        await callback.answer(i18n.get("ntf-schedule.no-schedule"))
        return
    weekday = datetime_now().weekday()
    if weekday >= len(user_schedule.days):
        await callback.answer(i18n.get("ntf-schedule.weekend", today=True))
        return

    await callback.answer(text=i18n.get("loading"))
    await notification_service.notify_user(user, MessagePayloadDto(
        i18n_key="ntf-schedule.today",
        i18n_kwargs={"text": user_schedule.days[weekday].text},
        delete_after=None,
        reply_markup=get_time_keyboard(),
    ))
    return


@inject
async def on_get_tomorrow(
    callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
    i18n: FromDishka[TranslatorRunner],
    user_service: FromDishka[UserService],
    notification_service: FromDishka[NotificationService],
) -> None:
    user: UserDto = dialog_manager.middleware_data[USER_KEY]
    user_schedule = await user_service.get_schedule(user)

    if not user_schedule:
        await callback.answer(i18n.get("ntf-schedule.no-schedule"))
        return
    weekday = (datetime_now() + timedelta(days=1)).weekday()
    if weekday >= len(user_schedule.days):
        await callback.answer(i18n.get("ntf-schedule.weekend"))
        return

    await callback.answer(text=i18n.get("loading"))
    await notification_service.notify_user(user, MessagePayloadDto(
        i18n_key="ntf-schedule.tomorrow",
        i18n_kwargs={"text": user_schedule.days[weekday].text},
        delete_after=None,
        reply_markup=get_time_keyboard(),
    ))
    return


@inject
async def on_get_week(
    callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
    i18n: FromDishka[TranslatorRunner],
    user_service: FromDishka[UserService],
    notification_service: FromDishka[NotificationService],
) -> None:
    user: UserDto = dialog_manager.middleware_data[USER_KEY]
    user_schedule = await user_service.get_schedule(user)

    if not user_schedule:
        await callback.answer(i18n.get("ntf-schedule.no-schedule"))
        return

    await callback.answer(text=i18n.get("loading"))
    await notification_service.notify_user(user, MessagePayloadDto(
        i18n_key="ntf-schedule.week",
        i18n_kwargs={"text": user_schedule.text},
        delete_after=None,
    ))
    return


@inject
async def on_get_year(
    callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
    i18n: FromDishka[TranslatorRunner],
    schedules_extra_service: FromDishka[SchedulesExtraService],
    notification_service: FromDishka[NotificationService],
) -> None:
    user: UserDto = dialog_manager.middleware_data[USER_KEY]
    schedules_extra = await schedules_extra_service.get()
    if not schedules_extra.year_photo_id:
        await callback.answer(i18n.get("ntf-error.year-missed"))
        await notification_service.notify_super_dev(MessagePayloadDto(
            i18n_key="ntf-error.year-missed",
            delete_after=None,
        ))
        return

    await callback.answer(text=i18n.get("loading"))
    await notification_service.notify_user(user, MessagePayloadDto(
        i18n_key="ntf-schedule.year",
        media_type=MediaType.PHOTO,
        media=MediaDescriptorDto("file_id", schedules_extra.year_photo_id),
        delete_after=None,
    ))
    return


@inject
async def on_day_request(
    message: Message,
    widget: MessageInput,
    dialog_manager: DialogManager,
    user_service: FromDishka[UserService],
    notification_service: FromDishka[NotificationService],
) -> None:
    user: UserDto = dialog_manager.middleware_data[USER_KEY]
    user_schedule = await user_service.get_schedule(user)

    if not user_schedule:
        await notification_service.notify_user(user, MessagePayloadDto(
            i18n_key="ntf-schedule.no-schedule",
            reply_markup=get_register_grade_keyboard(user.telegram_id),
            disable_default_markup=False,
        ))
        return

    if message.text not in user_schedule.list_days:
        await notification_service.notify_user(user, MessagePayloadDto(
            i18n_key="ntf-schedule.not-found",
            disable_default_markup=False,
        ))
        return

    day_index = user_schedule.list_days.index(message.text)
    schedule_day = user_schedule.days[day_index]

    await notification_service.notify_user(user, MessagePayloadDto(
        i18n_key="ntf-schedule.day",
        i18n_kwargs={"day": message.text, "text": schedule_day.text},
        reply_markup=get_time_keyboard(),
        delete_after=None,
    ))
    return


@inject
async def on_room_request(
    message: Message,
    widget: MessageInput,
    dialog_manager: DialogManager,
    schedule_service: FromDishka[ScheduleService],
    notification_service: FromDishka[NotificationService],
) -> None:
    user: UserDto = dialog_manager.middleware_data[USER_KEY]

    if not message.text or not message.text.startswith(InlineQueryText.ROOMS):
        await notification_service.notify_user(user, MessagePayloadDto(
            i18n_key="ntf-schedule.not-found",
            disable_default_markup=False,
        ))
        return
    room_schedule_id = int(message.text.split("_")[1])
    room_schedule = await schedule_service.get(room_schedule_id)

    if not room_schedule:
        await notification_service.notify_user(user, MessagePayloadDto(
            i18n_key="ntf-schedule.not-found",
            disable_default_markup=False,
        ))
        return

    await notification_service.notify_user(user, MessagePayloadDto(
        i18n_key="ntf-schedule.day",
        i18n_kwargs={"day": message.text, "text": room_schedule.text},
        reply_markup=get_time_keyboard(),
        delete_after=None
    ))
    return


@inject
async def on_free_rooms_day_selected(
    callback: CallbackQuery,
    widget: Select,
    dialog_manager: DialogManager,
    day_number: int,
    i18n: FromDishka[TranslatorRunner],
    schedule_service: FromDishka[ScheduleService],
    notification_service: FromDishka[NotificationService],
) -> None:
    user: UserDto = dialog_manager.middleware_data[USER_KEY]
    free_rooms = await schedule_service.get_free_rooms(day_number)

    await callback.answer()
    await dialog_manager.done()
    await notification_service.notify_user(user, MessagePayloadDto(
        i18n_key="ntf-schedule.free-rooms",
        i18n_kwargs={"day":WeekDay.str_list(i18n)[day_number], "text":free_rooms}
    ))


@inject
async def on_become_admin(
    callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
    i18n: FromDishka[TranslatorRunner],
    user_service: FromDishka[UserService],
    config: FromDishka[AppConfig],
    notification_service: FromDishka[NotificationService],
) -> None:
    user: UserDto = dialog_manager.middleware_data[USER_KEY]
    if user.role.includes(UserRole.ADMIN):
        await callback.answer(i18n.get("ntf-error.already-admin"))
        return

    owner = await user_service.get(config.bot.owner_id)
    await notification_service.notify_user(user, MessagePayloadDto(
        i18n_key="ntf-become-admin",
        i18n_kwargs={"owner":owner.mention if owner else ""},
        delete_after=15
    ))
    await callback.answer()
