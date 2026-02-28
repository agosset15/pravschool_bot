from types import TracebackType
from typing import Optional, Self, Type

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .repositories import (
    BroadcastRepository,
    ScheduleRepository,
    SchedulesExtraRepository,
    UserRepository,
)


class UnitOfWork:
    def __init__(self, session_maker: async_sessionmaker[AsyncSession]) -> None:
        self.session_maker = session_maker
        self.session: Optional[AsyncSession] = None
        self.users: UserRepository
        self.schedules: ScheduleRepository
        self.broadcasts: BroadcastRepository
        self.schedules_extra: SchedulesExtraRepository

    async def __aenter__(self) -> Self:
        self.session = self.session_maker()
        self.users = UserRepository(self.session)
        self.schedules = ScheduleRepository(self.session)
        self.broadcasts = BroadcastRepository(self.session)
        self.schedules_extra = SchedulesExtraRepository(self.session)

        logger.debug(f"SQL session started. Session ID: '{id(self.session)}'")
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        if self.session is None:
            return

        try:
            if exc_type:
                await self.session.rollback()
                logger.warning(f"SQL transaction rolled back due to error: '{exc_val}'")
            else:
                await self.session.commit()
                logger.debug("SQL transaction committed successfully")
        finally:
            await self.session.close()
            self.session = None
            self._repository = None
            logger.debug("SQL session closed")

    async def commit(self) -> None:
        if self.session:
            await self.session.commit()
            logger.debug(f"Session '{id(self.session)}' committed")

    async def rollback(self) -> None:
        if self.session:
            await self.session.rollback()
            logger.debug(f"Session '{id(self.session)}' rolled back")
