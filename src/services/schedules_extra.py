from typing import Optional

from adaptix import Retort
from adaptix.conversion import ConversionRetort
from aiogram import Bot
from loguru import logger
from redis.asyncio import Redis

from src.core.config import AppConfig
from src.core.constants import TTL_12H
from src.core.dto import SchedulesExtraDto
from src.infrastructure.cache import invalidate_cache, provide_cache
from src.infrastructure.cache.keys import SCHEDULES_EXTRA_PREFIX
from src.infrastructure.db import UnitOfWork
from src.infrastructure.db.models import SchedulesExtra

from .base import BaseService


class SchedulesExtraService(BaseService):
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
    ) -> None:
        super().__init__(config, bot, redis, retort, conversion_retort)
        self.uow = uow

        self._convert_to_dto = self.conversion_retort.get_converter(
            SchedulesExtra, SchedulesExtraDto
        )

    async def create_default(self) -> SchedulesExtraDto:
        db_schedules_extra = SchedulesExtra(**self.retort.dump(SchedulesExtraDto()))

        async with self.uow:
            db_created_schedules_extra = await self.uow.schedules_extra.create(db_schedules_extra)

        logger.info("Created default settings")
        return self._convert_to_dto(db_created_schedules_extra)

    @provide_cache(prefix=SCHEDULES_EXTRA_PREFIX, ttl=TTL_12H)
    async def get(self) -> SchedulesExtraDto:
        async with self.uow:
            db_schedules_extra = await self.uow.schedules_extra.get()

        if not db_schedules_extra:
            return await self.create_default()

        return self._convert_to_dto(db_schedules_extra)

    @invalidate_cache(key_builder=SCHEDULES_EXTRA_PREFIX)
    async def update(self, schedules_extra: SchedulesExtraDto) -> Optional[SchedulesExtraDto]:
        if not schedules_extra.changed_data:
            return None

        assert schedules_extra.id
        async with self.uow:
            db_schedules_extra = await self.uow.schedules_extra.update(
                schedules_extra.id,
                **schedules_extra.changed_data
            )

        return self._convert_to_dto(db_schedules_extra)  # ty:ignore[invalid-argument-type]