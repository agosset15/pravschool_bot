from dataclasses import asdict
from typing import Optional
from uuid import UUID

from adaptix import Retort
from adaptix.conversion import ConversionRetort
from aiogram import Bot
from fluentogram import TranslatorHub
from loguru import logger
from redis.asyncio import Redis
from sqlalchemy import and_

from src.core.config import AppConfig
from src.core.dto import BroadcastDto, BroadcastMessageDto, UserDto
from src.core.enums import BroadcastAudience, BroadcastStatus, UserRole
from src.infrastructure.db import UnitOfWork
from src.infrastructure.db.models import Broadcast, BroadcastMessage, User

from .base import BaseService


class BroadcastService(BaseService):
    uow: UnitOfWork

    def __init__(
        self,
        config: AppConfig,
        bot: Bot,
        redis: Redis,
        retort: Retort,
        conversion_retort: ConversionRetort,
        #
        translator_hub: TranslatorHub,
        uow: UnitOfWork,
    ) -> None:
        super().__init__(config, bot, redis, retort, conversion_retort)
        self.translator_hub = translator_hub
        self.uow = uow

        self._convert_to_dto = self.conversion_retort.get_converter(Broadcast, BroadcastDto)
        self._convert_to_dto_list = self.conversion_retort.get_converter(
            list[Broadcast], list[BroadcastDto]
        )

    async def create(self, broadcast: BroadcastDto) -> BroadcastDto:
        broadcast_data = self.retort.dump(broadcast)
        db_broadcast = Broadcast(**broadcast_data)

        async with self.uow:
            db_created_broadcast = await self.uow.broadcasts.create(db_broadcast)

        logger.info(f"Created broadcast '{broadcast.task_id}'")
        return self._convert_to_dto(db_created_broadcast)

    async def create_messages(
        self,
        broadcast_id: int,
        messages: list[BroadcastMessageDto],
    ) -> None:
        db_messages = [
            BroadcastMessage(**self.retort.dump(msg), broadcast_id=broadcast_id) for msg in messages
        ]
        async with self.uow:
            await self.uow.broadcasts.create_messages(db_messages)

    async def get(self, task_id: UUID) -> Optional[BroadcastDto]:
        async with self.uow:
            db_broadcast = await self.uow.broadcasts.get(task_id)

        if db_broadcast:
            logger.debug(f"Retrieved broadcast '{task_id}'")
        else:
            logger.warning(f"Broadcast '{task_id}' not found")

        return self._convert_to_dto(db_broadcast)  # ty:ignore[invalid-argument-type]

    async def get_all(self) -> list[BroadcastDto]:
        async with self.uow:
            db_broadcasts = await self.uow.broadcasts.get_all()

        return self._convert_to_dto_list(list(reversed(db_broadcasts)))

    async def update(self, broadcast: BroadcastDto) -> Optional[BroadcastDto]:
        async with self.uow:
            db_updated_broadcast = await self.uow.broadcasts.update(
                task_id=broadcast.task_id,
                **broadcast.changed_data,
            )

        if db_updated_broadcast:
            logger.info(f"Updated broadcast '{broadcast.task_id}' successfully")
        else:
            logger.warning(
                f"Attempted to update broadcast '{broadcast.task_id}', "
                f"but broadcast was not found or update failed"
            )

        return self._convert_to_dto(db_updated_broadcast)  # ty:ignore[invalid-argument-type]

    async def update_message(self, broadcast_id: int, message: BroadcastMessageDto) -> None:
        async with self.uow:
            await self.uow.broadcasts.update_message(
                broadcast_id=broadcast_id,
                user_telegram_id=message.user_telegram_id,
                **message.changed_data,
            )

    async def bulk_update_messages(self, messages: list[BroadcastMessageDto]) -> None:
        async with self.uow:
            await self.uow.broadcasts.bulk_update_messages(
                data=[asdict(m) for m in messages],
            )

    async def delete_broadcast(self, broadcast_id: int) -> None:
        async with self.uow:
            await self.uow.broadcasts.delete(broadcast_id)

    async def get_status(self, task_id: UUID) -> Optional[BroadcastStatus]:
        async with self.uow:
            db_broadcast = await self.uow.broadcasts.get(task_id)

        return db_broadcast.status if db_broadcast else None

    #

    async def get_audience_count(
        self,
        audience: BroadcastAudience,
        plan_id: Optional[int] = None,
    ) -> int:
        logger.debug(f"Counting audience '{audience}' for plan '{plan_id}'")

        is_not_block = User.is_blocked.is_(False)

        if audience == BroadcastAudience.ALL:
            async with self.uow:
                result = await self.uow.users.count(is_not_block)
            return result

        if audience == BroadcastAudience.PARENTS:
            async with self.uow:
                result = await self.uow.users.count(and_(is_not_block, User.is_parent.is_(True)))
            return result

        if audience == BroadcastAudience.TEACHERS:
            async with self.uow:
                result = await self.uow.users.count(and_(is_not_block, User.is_teacher.is_(True)))
            return result

        if audience == BroadcastAudience.NS:
            async with self.uow:
                result = await self.uow.users.count(and_(is_not_block, User.is_ns.is_(True)))
            return result

        if audience == BroadcastAudience.ADMINS:
            async with self.uow:
                result = await self.uow.users.count(and_(
                    is_not_block, User.role.is_(UserRole.ADMIN)
                ))
            return result

        raise Exception(f"Unknown broadcast audience: {audience}")

    async def get_audience_users(
        self,
        audience: BroadcastAudience,
        plan_id: Optional[int] = None,
    ) -> list[UserDto]:
        logger.debug(f"Retrieving users for audience '{audience}', plan_id: {plan_id}")

        is_not_block = User.is_blocked.is_(False)
        convert_to_user_dto_list = self.conversion_retort.get_converter(
            list[User], list[UserDto]
        )

        if audience == BroadcastAudience.ALL:
            async with self.uow:
                db_users = await self.uow.users.get_all(is_not_block)

            return convert_to_user_dto_list(db_users)

        if audience == BroadcastAudience.PARENTS:
            async with self.uow:
                db_users = await self.uow.users.get_all(and_(
                    is_not_block, User.is_parent.is_(True)
                ))
            return convert_to_user_dto_list(db_users)

        if audience == BroadcastAudience.TEACHERS:
            async with self.uow:
                db_users = await self.uow.users.get_all(and_(
                    is_not_block, User.is_teacher.is_(True)
                ))
            return convert_to_user_dto_list(db_users)

        if audience == BroadcastAudience.NS:
            async with self.uow:
                db_users = await self.uow.users.get_all(and_(
                    is_not_block, User.is_ns.is_(True)
                ))
            return convert_to_user_dto_list(db_users)

        if audience == BroadcastAudience.ADMINS:
            async with self.uow:
                db_users = await self.uow.users.get_all(and_(
                    is_not_block, User.role.is_(UserRole.ADMIN)
                ))
            return convert_to_user_dto_list(db_users)

        raise Exception(f"Unknown broadcast audience: {audience}")