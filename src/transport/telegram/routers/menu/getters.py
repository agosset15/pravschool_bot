from typing import Any

from aiogram_dialog import DialogManager
from dishka.integrations.aiogram_dialog import FromDishka, inject
from fluentogram import TranslatorRunner

from src.core.config import AppConfig
from src.core.constants import REPOSITORY
from src.core.dto import UserDto
from src.core.enums import WeekDay
from src.services.user import UserService


@inject
async def menu_getter(
    dialog_manager: DialogManager,
    config: AppConfig,
    user: UserDto,
    **kwargs: Any,
) -> dict[str, Any]:
    return {
        "name": user.name,
        "grade": user.grade if user.grade else False,
        "is_teacher": user.is_teacher,
        "is_dev": user.role
    }

@inject
async def days_getter(
    dialog_manager: DialogManager,
    config: AppConfig,
    user: UserDto,
    i18n: FromDishka[TranslatorRunner],
    **kwargs: Any,
) -> dict[str, Any]:
    return {
        "days": list(enumerate(WeekDay.str_list(i18n)))
    }


@inject
async def bot_info_getter(
    dialog_manager: DialogManager,
    config: AppConfig,
    user: UserDto,
    user_service: FromDishka[UserService],
    **kwargs: Any,
) -> dict[str, Any]:
    admin = await user_service.get(config.bot.owner_id)
    count = await user_service.count()
    return {"count": count, "admin": admin.mention if admin else "", "repository": REPOSITORY}
