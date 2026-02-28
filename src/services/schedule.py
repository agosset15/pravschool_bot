from typing import Optional

from adaptix import Retort
from adaptix.conversion import ConversionRetort
from aiogram import Bot
from fluentogram import TranslatorRunner
from loguru import logger
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import AppConfig
from src.core.constants import LESSON_TIMES, TTL_7D
from src.core.dto import DayDto, ScheduleDto
from src.core.enums import ScheduleType
from src.infrastructure.cache import invalidate_cache, provide_cache
from src.infrastructure.cache.keys import ScheduleCacheKey, SchedulesListCacheKey
from src.infrastructure.db import UnitOfWork
from src.infrastructure.db.models import Day, Lesson, Schedule

from .base import BaseService


class ScheduleService(BaseService):
    uow: UnitOfWork

    def __init__(
        self,
        config: AppConfig,
        bot: Bot,
        redis: Redis,
        retort: Retort,
        conversion_retort: ConversionRetort,
        #
        uow: UnitOfWork,
        i18n: TranslatorRunner
    ) -> None:
        super().__init__(config, bot, redis, retort, conversion_retort)
        self.uow = uow
        self.i18n = i18n

        self._convert_to_dto = self.conversion_retort.get_converter(Schedule, ScheduleDto)
        self._convert_to_dto_list = self.conversion_retort.get_converter(
            list[Schedule], list[ScheduleDto]
        )

    @invalidate_cache(key_builder=["schedule", "schedules_list"])
    async def create_recursive(self, schedule: ScheduleDto) -> ScheduleDto:
        db_schedule = Schedule(**self.retort.dump(schedule))

        async with self.uow:
            db_created_schedule = await self.uow.schedules.create(db_schedule)
            for day in schedule.days:
                db_day = Day(schedule_id=db_created_schedule.id, **self.retort.dump(day))
                db_created_day = await self.uow.schedules.create_day(db_day)
                for lesson in day.lessons:
                    db_lesson = Lesson(
                        day_id=db_created_day.id, **self.retort.dump(lesson)
                    )
                    await self.uow.schedules.create_lesson(db_lesson)

        logger.info(f"Created new schedule type='{schedule.type}' grade='{schedule.grade}'")
        return self._convert_to_dto(db_created_schedule)

    @provide_cache(ttl=TTL_7D, key_builder=ScheduleCacheKey)
    async def get(self, schedule_id: int) -> Optional[ScheduleDto]:
        async with self.uow:
            db_schedule = await self.uow.schedules.get(schedule_id)

        if db_schedule:
            logger.debug(f"Retrieved schedule '{schedule_id}'")
        else:
            logger.warning(f"Schedule '{schedule_id}' not found")

        return self._convert_to_dto(db_schedule)

    async def get_day(self, day_id: int) -> Optional[DayDto]:
        async with self.uow:
            day = await self.uow.schedules.get_day(day_id)

        if not day:
            logger.warning(f"Day '{day_id}' not found")
            return None
        convert = self.conversion_retort.get_converter(Day, DayDto)
        return convert(day)

    @invalidate_cache(key_builder=["schedule", "schedules_list"])
    async def update(self, schedule: ScheduleDto) -> Optional[ScheduleDto]:
        async with self.uow:
            db_updated_schedule = await self.uow.schedules.update(
                telegram_id=schedule.id,
                **schedule.changed_data,
            )

        if db_updated_schedule:
            logger.info(f"Updated schedule '{schedule.id}' successfully")
        else:
            logger.warning(
                f"Attempted to update schedule '{schedule.id}', "
                f"but schedule was not found or update failed"
            )

        return self._convert_to_dto(db_updated_schedule)

    @invalidate_cache(key_builder=["schedule", "schedules_list"])
    async def delete(self, schedule: ScheduleDto) -> bool:
        async with self.uow:
            result = await self.uow.schedules.delete(schedule.id)

        logger.info(f"Deleted schedule '{schedule.id}': '{result}'")
        return result

    @invalidate_cache(key_builder=["schedule", "schedules_list"])
    async def delete_all(self) -> bool:
        async with self.uow:
            result = await self.uow.schedules.delete_all()

        logger.info(f"Deleted all schedules: '{result}'")
        return result

    @provide_cache(ttl=TTL_7D, key_builder=SchedulesListCacheKey)
    async def find_by_type_partial_grade(
            self, schedule_type: ScheduleType, grade: str
    ) -> list[ScheduleDto]:
        async with self.uow:
            db_schedules = await self.uow.schedules.get_by_partial_grade(grade, schedule_type)

        logger.debug(f"Retrieved schedules for type '{schedule_type}' containing grade '{grade}'")
        return self._convert_to_dto_list(db_schedules)

    @provide_cache(ttl=TTL_7D, key_builder=SchedulesListCacheKey)
    async def get_all_by_type(self, schedule_type: ScheduleType) -> list[ScheduleDto]:
        async with self.uow:
            db_schedules = await self.uow.schedules.get_all_by_type(schedule_type)

        logger.debug(f"Retrieved schedules for type '{schedule_type}'")
        return self._convert_to_dto_list(db_schedules)

    async def get_grades(self, schedule_type: ScheduleType, inline_extra: bool = False) -> set[str]:
        lst = {schedule.grade for schedule in await self.get_all_by_type(schedule_type)}
        if inline_extra:
            lst.update(["".join(filter(str.isdigit, grade)) for grade in lst])
        return lst

    async def get_free_rooms(self, day_number: int) -> str:
        rooms = await self.get_all_by_type(ScheduleType.ROOM)
        text = []
        for lesson_number, rooms in enumerate(self._find_free(rooms)[day_number]):
            text.append(
                f"<b>{lesson_number + 1}</b> ({LESSON_TIMES[lesson_number]}):\n{', '.join(rooms)}"
            )
        return "\n\n".join(text)

    async def parse_homeworks(self, day_id: int) -> list[str]:
        homeworks: list[str] = []
        day = await self.get_day(day_id)
        if day is None:
            return []

        for lesson in day.lessons:
            if not lesson.homework:
                homeworks.append(f"<b>{lesson.name}</b> - {self.i18n.get('no')}")
            else:
                hw_text = (
                    f"<b>{lesson.name}</b> - {lesson.homework.text}"
                    f"({self.i18n.get('added')} "
                    f"{lesson.homework.updated_at.strftime('%d-%m-%Y, %H:%M')})"
                )
                if lesson.homework.image:
                    hw_text += self.i18n.get("photos-only-in-bot")
                homeworks.append(hw_text)
        return homeworks

    def _find_free(self, schedules: list[ScheduleDto]) -> list[list[list[str]]]:
        r = [[[] for _1 in range(10)] for _ in range(6)]
        for schedule in schedules:
            for day_number, day in enumerate(schedule.days):
                for lesson_number, lesson_text in enumerate(day.lessons_list):
                    if lesson_text:
                        r[day_number][lesson_number].append(lesson_text)
        return r