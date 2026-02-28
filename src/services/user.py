from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, cast

from adaptix import Retort
from adaptix.conversion import ConversionRetort
from aiogram import Bot
from aiogram.types import Message
from aiogram.types import User as AiogramUser
from loguru import logger
from redis.asyncio import Redis
from sqlalchemy import select

from src.core.config import AppConfig
from src.core.constants import TTL_5M, TTL_10M
from src.core.dto import ScheduleDto, UserDto
from src.core.enums import UserRole
from src.infrastructure.cache import invalidate_cache, provide_cache
from src.infrastructure.cache.keys import (
    USER_COUNT_PREFIX,
    USER_LIST_PREFIX,
    ScheduleCacheKey,
    UserCacheKey,
)
from src.infrastructure.db import UnitOfWork
from src.infrastructure.db.models import Schedule, User

from .base import BaseService


class UserService(BaseService):
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

        self._convert_to_dto = self.conversion_retort.get_converter(User, UserDto)
        self._convert_to_dto_list = self.conversion_retort.get_converter(list[User], list[UserDto])

    @invalidate_cache(key_builder=[USER_COUNT_PREFIX, USER_LIST_PREFIX])
    @invalidate_cache(key_builder=UserCacheKey)
    async def create(self,
                     aiogram_user: AiogramUser,
                     referral_code: Optional[str] = None
                     ) -> UserDto:
        user = UserDto(
            telegram_id=aiogram_user.id,
            username=aiogram_user.username,
            referral_code=referral_code,
            name=aiogram_user.full_name,
        )
        db_user = User(**self.retort.dump(user))

        async with self.uow:
            db_created_user = await self.uow.users.create(db_user)

        logger.info(f"Created new user '{user.telegram_id}'")
        return self._convert_to_dto(db_created_user)

    @provide_cache(ttl=TTL_5M, key_builder=UserCacheKey)
    async def get(self, telegram_id: int) -> Optional[UserDto]:
        async with self.uow:
            db_user = await self.uow.users.get(telegram_id)

        if db_user:
            logger.debug(f"Retrieved user '{telegram_id}'")
            return self._convert_to_dto(db_user)

        else:
            logger.warning(f"User '{telegram_id}' not found")
            return None

    @invalidate_cache(key_builder=[USER_COUNT_PREFIX, USER_LIST_PREFIX])
    @invalidate_cache(key_builder=UserCacheKey)
    async def update(self, user: UserDto) -> Optional[UserDto]:
        async with self.uow:
            db_updated_user = await self.uow.users.update(
                telegram_id=user.telegram_id,
                **user.changed_data,
            )

        if db_updated_user:
            logger.info(f"Updated user '{user.telegram_id}' successfully")
        else:
            logger.warning(
                f"Attempted to update user '{user.telegram_id}', "
                f"but user was not found or update failed"
            )

        return self._convert_to_dto(db_updated_user)

    @invalidate_cache(key_builder=[USER_COUNT_PREFIX, USER_LIST_PREFIX])
    @invalidate_cache(key_builder=UserCacheKey)
    async def delete(self, user: UserDto) -> bool:
        async with self.uow:
            result = await self.uow.users.delete(user.telegram_id)

        logger.info(f"Deleted user '{user.telegram_id}': '{result}'")
        return result

    async def get_by_partial_name(self, query: str) -> list[UserDto]:
        async with self.uow:
            db_users = await self.uow.users.get_by_partial_name(query)

        logger.debug(f"Retrieved '{len(db_users)}' users for query '{query}'")
        return self._convert_to_dto_list(db_users)

    async def get_by_referral_code(self, referral_code: str) -> list[UserDto]:
        async with self.uow:
            user = await self.uow.users.get_by_referral_code(referral_code)

        return self._convert_to_dto_list(user)

    @provide_cache(ttl=TTL_10M, key_builder=ScheduleCacheKey)
    async def get_schedule(self, user: UserDto) -> Optional[ScheduleDto]:
        if not user.schedule_id:
            return None
        async with self.uow:
            schedule = await self.uow.schedules.get_with_days(user.schedule_id)
        schedule_converter = self.conversion_retort.get_converter(Schedule, ScheduleDto)
        return schedule_converter(schedule)  # ty:ignore[invalid-argument-type]

    @provide_cache(prefix=USER_COUNT_PREFIX, ttl=TTL_10M)
    async def count(self) -> int:
        async with self.uow:
            count = await self.uow.users.count()

        logger.debug(f"Total users count: '{count}'")
        return count

    async def get_blocked_users(self) -> list[UserDto]:
        async with self.uow:
            db_users = await self.uow.users.filter_by_blocked(blocked=True)

        logger.debug(f"Retrieved '{len(db_users)}' blocked users")
        return self._convert_to_dto_list(list(reversed(db_users)))

    async def get_by_role(self, role: UserRole) -> list[UserDto]:
        async with self.uow:
            db_users = await self.uow.users.filter_by_role(role)

        logger.debug(f"Retrieved '{len(db_users)}' users with role '{role}'")
        return self._convert_to_dto_list(db_users)

    @provide_cache(ttl=TTL_10M, prefix=USER_LIST_PREFIX)
    async def get_all(self) -> list[UserDto]:
        async with self.uow:
            db_users = await self.uow.users.get_all()

        logger.debug(f"Retrieved '{len(db_users)}' users")
        return self._convert_to_dto_list(db_users)

    @invalidate_cache(key_builder=UserCacheKey)
    async def set_block(self, user: UserDto, blocked: bool) -> None:
        user.is_blocked = blocked

        async with self.uow:
            await self.uow.users.update(
                user.telegram_id,
                **user.changed_data,
            )

        logger.info(f"Set block={blocked} for user '{user.telegram_id}'")

    @invalidate_cache(key_builder=UserCacheKey)
    async def set_admin(self, user: UserDto, is_admin: bool) -> None:
        user.is_admin = is_admin

        async with self.uow:
            await self.uow.users.update(
                user.telegram_id,
                **user.changed_data,
            )

        logger.info(f"Set is_admin={is_admin} for user '{user.telegram_id}'")

    @invalidate_cache(key_builder=UserCacheKey)
    async def set_ns(self, user: UserDto,
                     is_ns: bool) -> None:
        user.is_ns = is_ns

        async with self.uow:
            await self.uow.users.update(
                user.telegram_id,
                **user.changed_data,
            )

        logger.info(f"Set is_ns={is_ns} for user '{user.telegram_id}'")

    @invalidate_cache(key_builder=UserCacheKey)
    async def set_ns_credentials(self, user: UserDto,
                               login: Optional[str] = None,
                               password: Optional[bytes] = None) -> None:
        user.login = login
        user.password = password

        async with self.uow:
            await self.uow.users.update(
                user.telegram_id,
                **user.changed_data,
            )

        logger.info(f"Set login={login} and password for user '{user.telegram_id}'")

    @invalidate_cache(key_builder=UserCacheKey)
    async def set_schedule(self, user: UserDto, schedule_id: int) -> None:
        async with self.uow:
            await self.uow.users.update(
                telegram_id=user.telegram_id,
                schedule_id=schedule_id,
            )

        logger.info(f"Set schedule='{schedule_id}' for user '{user.telegram_id}'")

    @invalidate_cache(key_builder=UserCacheKey)
    async def delete_schedule(self, user: UserDto) -> None:
        async with self.uow:
            await self.uow.users.update(
                telegram_id=user.telegram_id,
                schedule_id=None,
            )

        logger.info(f"Delete current schedule for user '{user.telegram_id}'")

    #

    async def get_recent_activity_users(
        self,
        excluded_ids: Optional[list[int]] = None,
    ) -> list[UserDto]:
        stmt = select(User)

        if excluded_ids:
            stmt = stmt.where(User.telegram_id.not_in(excluded_ids))

        stmt = stmt.order_by(User.updated_at.desc().nulls_last()).limit(10)
        async with self.uow:
            session = cast(AsyncSession, self.uow.session)
            result = await session.execute(stmt)
        db_users = result.scalars().all()

        logger.debug(f"Retrieved '{len(db_users)}' users with recent activity")
        return self._convert_to_dto_list(list(db_users))

    async def get_recent_registered_users(self, limit: int = 5) -> list[UserDto]:
        stmt = select(User).order_by(User.created_at.desc()).limit(limit)
        async with self.uow:
            session = cast(AsyncSession, self.uow.session)
            result = await session.execute(stmt)
        db_users = result.scalars().all()

        logger.debug(f"Retrieved '{len(db_users)}' recently registered users")
        return self._convert_to_dto_list(list(db_users))

    async def search_users(self, message: Message) -> list[UserDto]:
        found_users = []

        if message.forward_from and not message.forward_from.is_bot:
            target_telegram_id = message.forward_from.id
            single_user = await self.get(telegram_id=target_telegram_id)

            if single_user:
                found_users.append(single_user)
                logger.info(f"Search by forwarded message, found user '{target_telegram_id}'")
            else:
                logger.warning(
                    f"Search by forwarded message, user '{target_telegram_id}' not found"
                )

        elif message.text:
            search_query = message.text.strip()
            logger.debug(f"Searching users by query '{search_query}'")

            if search_query.isdigit():
                target_telegram_id = int(search_query)
                single_user = await self.get(telegram_id=target_telegram_id)

                if single_user:
                    found_users.append(single_user)
                    logger.info(f"Searched by Telegram ID '{target_telegram_id}', user found")
                else:
                    logger.warning(
                        f"Searched by Telegram ID '{target_telegram_id}', user not found"
                    )
            else:
                found_users = await self.get_by_partial_name(query=search_query)
                logger.info(
                    f"Searched users by partial name '{search_query}', "
                    f"found '{len(found_users)}' users"
                )

        return found_users