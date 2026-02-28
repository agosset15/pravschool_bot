from aiogram import F, Router
from aiogram.filters import MagicData
from aiogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from dishka.integrations.aiogram_dialog import FromDishka, inject
from fluentogram import TranslatorRunner
from loguru import logger

from src.core.config import AppConfig
from src.core.constants import TTL_10M
from src.core.dto import UserDto
from src.core.enums import InlineQueryText, ScheduleType
from src.services.bot import BotService
from src.services.schedule import ScheduleService
from src.services.user import UserService
from src.transport.telegram.keyboards import inline_grade_results, inline_schedule_results, url_kb
from src.transport.telegram.states import MainMenu, Register

router = Router(name=__name__)


@inject
@router.inline_query(MagicData(F.query.in_(F.grades)))
async def inline_grade_schedule(
        query: InlineQuery,
        user: UserDto,
        config: FromDishka[AppConfig],
        bot_service: FromDishka[BotService],
        i18n: FromDishka[TranslatorRunner],
        schedule_service: FromDishka[ScheduleService],
):
    logger.info(f"Inline reached: {query.query}")
    schedules = await schedule_service.find_by_type_partial_grade(ScheduleType.COMMON, query.query)
    bot_link = await bot_service.get_referral_url("inline-ref-btn")
    kbd = url_kb(**{bot_link: i18n.get("inline-ref-btn")})

    await query.answer(
        inline_grade_results(schedules[0], i18n, config, kbd),
        cache_time=TTL_10M,
        is_personal=False,
        switch_pm_text=schedules[0].grade,
        switch_pm_parameter=f"{query.query}_inline",
    )

@inject
@router.inline_query(Register.GRADE, F.query.startswith(InlineQueryText.TEACHERS))
async def inline_teachers(
        query: InlineQuery,
        schedule_service: FromDishka[ScheduleService],
):
    name = query.query.removeprefix(InlineQueryText.TEACHERS)
    teachers = await schedule_service.find_by_type_partial_grade(ScheduleType.TEACHER, name)
    await query.answer(
        inline_schedule_results(teachers, InlineQueryText.TEACHERS),
        is_personal=False,
        cache_time=TTL_10M,
    )

@inject
@router.inline_query(Register.GRADE, F.query.startswith(InlineQueryText.GRADES))
async def inline_grades(
        query: InlineQuery,
        schedule_service: FromDishka[ScheduleService],
):
    grade = query.query.removeprefix(InlineQueryText.GRADES)
    grades = await schedule_service.find_by_type_partial_grade(ScheduleType.COMMON, grade)
    await query.answer(
        inline_schedule_results(grades, InlineQueryText.GRADES),
        is_personal=False,
        cache_time=TTL_10M,
    )


@inject
@router.inline_query(MainMenu.ROOMS, F.query.startswith(InlineQueryText.ROOMS))
async def inline_rooms(
        query: InlineQuery,
        schedule_service: FromDishka[ScheduleService],
):
    room = query.query.removeprefix(InlineQueryText.ROOMS)
    rooms = await schedule_service.find_by_type_partial_grade(ScheduleType.ROOM, room)
    await query.answer(
        inline_schedule_results(rooms, InlineQueryText.ROOMS),
        is_personal=False,
        cache_time=TTL_10M,
    )



@inject
@router.inline_query()
async def inline_day(
        query: InlineQuery,
        user: UserDto,
        config: FromDishka[AppConfig],
        bot_service: FromDishka[BotService],
        i18n: FromDishka[TranslatorRunner],
        user_service: FromDishka[UserService],
):
    schedule = await user_service.get_schedule(user)
    if user.grade == 0 or not schedule:
        buttons = [
            InlineQueryResultArticle(
                id="err",
                title=i18n.get("err-not-registered.title"),
                description=i18n.get("err-not-registered.description"),
                input_message_content=InputTextMessageContent(message_text=i18n.get("ntf-error.unknown"))
            )]
        return await query.answer(
            buttons, cache_time=1, is_personal=True,
            switch_pm_parameter="inline", switch_pm_text=i18n.get("ntf-registration")
        )
    bot_link = await bot_service.get_referral_url("inline-ref-btn")
    kbd = url_kb(**{bot_link: i18n.get("inline-ref-btn")})
    return await query.answer(
        inline_grade_results(schedule, i18n, config, kbd),
        cache_time=TTL_10M,
        is_personal=True,
        switch_pm_text=schedule.grade,
        switch_pm_parameter=f"{query.query}_inline"
    )
