from typing import Any, Optional

from src.core.enums import ScheduleType
from src.infrastructure.db.models import Day, Lesson, Schedule

from .base import BaseRepository


class ScheduleRepository(BaseRepository):
    async def create(self, schedule: Schedule) -> Schedule:
        return await self.create_instance(schedule)

    async def create_day(self, day: Day) -> Day:
        return await self.create_instance(day)

    async def create_lesson(self, lesson: Lesson) -> Lesson:
        return await self.create_instance(lesson)

    async def get(self, schedule_id: int) -> Optional[Schedule]:
        return await self._get_one(Schedule, Schedule.id == schedule_id)

    async def get_with_days(self, schedule_id: int) -> Optional[Schedule]:
        return await self._get_one(Schedule, Schedule.id == schedule_id, joined=Schedule.days)

    async def get_day(self, day_id: int) -> Optional[Day]:
        return await self._get_one(Day, Day.id == day_id, joined=Lesson.homework)

    async def get_by_type_grade(
            self, schedule_type: ScheduleType, grade: str
    ) -> Optional[Schedule]:
        return await self._get_one(
            Schedule, Schedule.type == schedule_type, Schedule.grade == grade
        )

    async def get_all(self) -> list[Schedule]:
        return await self._get_many(Schedule)

    async def get_all_by_type(self, schedule_type: ScheduleType) -> list[Schedule]:
        return await self._get_many(Schedule, Schedule.type == schedule_type)

    async def get_by_partial_grade(self, query: str, schedule_type: ScheduleType) -> list[Schedule]:
        return await self._get_many(
            Schedule, Schedule.grade.contains(query.lower()), Schedule.type == schedule_type
        )

    async def update(self, schedule_id: int, **data: Any) -> Optional[Schedule]:
        return await self._update(Schedule, Schedule.id == schedule_id, **data)

    async def delete(self, schedule_id: int) -> bool:
        return bool(await self._delete(Schedule, Schedule.id == schedule_id))

    async def delete_all(self) -> bool:
        return bool(await self._delete(Schedule))
