from datetime import date, timedelta
from typing import Any

from aiogram_dialog import DialogManager
from dishka.integrations.aiogram_dialog import FromDishka, inject
from fluentogram import TranslatorRunner

from src.core.config import AppConfig
from src.core.dto import UserDto
from src.core.enums import Month, WeekDay
from src.core.utils import date_now
from src.services.bot import BotService
from src.services.netschool import NetSchoolService


@inject
async def ns_menu_getter(
    dialog_manager: DialogManager,
    config: AppConfig,
    user: UserDto,
    i18n: FromDishka[TranslatorRunner],
    bot_service: FromDishka[BotService],
    **kwargs: Any,
) -> dict[str, Any]:
    start = date_now() - timedelta(days=date_now().weekday())
    end = start + timedelta(days=6)
    days_texts = WeekDay.str_list(i18n)
    for i, day in enumerate(days_texts):
        now = start + timedelta(days=i)
        days_texts[i] = f"{day} ({now.day} {Month(now.month).get_text_possessive(i18n)})"
    dialog_manager.dialog_data["start"] = start
    dialog_manager.dialog_data["end"] = end

    return {
        "is_ns": user.is_ns,
        "week": start.strftime("%d.%m.%Y") + " - " + end.strftime("%d.%m.%Y"),
        "days": list(enumerate(days_texts)),
        "mini_app_url": await bot_service.get_mini_app_url(),
    }

@inject
async def ns_day_getter(
    dialog_manager: DialogManager,
    config: AppConfig,
    user: UserDto,
    netschool_service: FromDishka[NetSchoolService],
    **kwargs: Any,
) -> dict[str, Any]:
    day: date = dialog_manager.dialog_data["day"]
    day_text = await netschool_service.get_day(user, user.default_child, day)
    children = await netschool_service.get_students(user)
    student = children[0]
    for child in children:
        if child.id == user.default_child:
            student = child

    return {
        "children": children if user.is_parent else False,
        "student_id": student.id,
        "day_text": day_text,
    }
