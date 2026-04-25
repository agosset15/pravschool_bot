from typing import Any

from aiogram_dialog import DialogManager
from dishka.integrations.aiogram_dialog import FromDishka, inject
from fluentogram import TranslatorRunner

from src.core.config import AppConfig
from src.core.constants import REPOSITORY
from src.core.dto import UserDto
from src.core.enums import WeekDay
from src.services.netschool import NetSchoolService
from src.services.user import UserService


@inject
async def menu_getter(
    dialog_manager: DialogManager,
    config: AppConfig,
    user: UserDto,
    **kwargs: Any,
) -> dict[str, Any]:
    start_user_grade = None
    if isinstance(dialog_manager.start_data, dict):
        start_user_grade = dialog_manager.start_data.get("grade", None)
    return {
        "name": user.name,
        "grade": start_user_grade or user.grade or False,
        "is_teacher": user.is_teacher,
        "is_dev": user.role,
    }


@inject
async def days_getter(
    dialog_manager: DialogManager,
    config: AppConfig,
    user: UserDto,
    i18n: FromDishka[TranslatorRunner],
    **kwargs: Any,
) -> dict[str, Any]:
    return {"days": list(enumerate(WeekDay.str_list(i18n)))}


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


@inject
async def students_getter(
    dialog_manager: DialogManager,
    config: AppConfig,
    user: UserDto,
    netschool_service: FromDishka[NetSchoolService],
    **kwargs: Any,
) -> dict[str, Any]:
    children = await netschool_service.get_students(user)

    return {"children": children if user.is_parent else False, "selected": user.default_child}
