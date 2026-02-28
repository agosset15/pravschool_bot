from typing import Any, Optional

from src.infrastructure.db.models import SchedulesExtra

from .base import BaseRepository


class SchedulesExtraRepository(BaseRepository):
    async def create(self, schedules_extra: SchedulesExtra) -> SchedulesExtra:
        return await self.create_instance(schedules_extra)

    async def get(self) -> Optional[SchedulesExtra]:
        return await self._get_one(SchedulesExtra, limit=1)

    async def update(self, schedules_extra_id: int, **data: Any) -> Optional[SchedulesExtra]:
        return await self._update(SchedulesExtra, SchedulesExtra.id == schedules_extra_id, **data)
