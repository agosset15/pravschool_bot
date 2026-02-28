import asyncio
from datetime import date
from typing import List, Optional, TypeVar, cast

from adaptix import Retort
from adaptix.conversion import ConversionRetort
from aiogram import Bot
from aiogram.types import BufferedInputFile
from aiogram.utils.link import create_telegram_link
from fluentogram import TranslatorRunner
from redis.asyncio import Redis

from src.core.config import AppConfig
from src.core.constants import TTL_7D, TTL_10M
from src.core.dto import StudentDto, UserDto
from src.core.exceptions import (
    AssignmentNotFoundError,
    AuthError,
    DayNotFoundError,
    LessonNotFoundError,
    NoResponseFromServerError,
)
from src.core.utils.crypto import encode_ns_password, get_ns_request_hash
from src.infrastructure.cache import invalidate_cache, provide_cache
from src.infrastructure.cache.keys import NetschoolResponseKey, UserCacheKey
from src.infrastructure.db import UnitOfWork
from src.infrastructure.http import NetSchoolAPI
from src.infrastructure.http.schemas import Assignment, Day, NetSchoolAPISchema, Student
from src.services.base import BaseService
from src.services.bot import BotService

from .api_factory import NetSchoolApiFactory

T = TypeVar("T", bound=NetSchoolAPISchema)


class NetSchoolService(BaseService):
    def __init__(
            self,
            config: AppConfig,
            bot: Bot,
            redis: Redis,
            retort: Retort,
            conversion_retort: ConversionRetort,
            #
            uow: UnitOfWork,
            api_factory: NetSchoolApiFactory,
            i18n: TranslatorRunner,
            bot_service: BotService,
    ):
        super().__init__(config, bot, redis, retort, conversion_retort)
        self.uow = uow
        self.api_factory = api_factory
        self.i18n = i18n
        self.bot_service = bot_service
        self._api: Optional[NetSchoolAPI] = None

    async def _get_api(self, user: UserDto) -> NetSchoolAPI:
        if not self._api:
            if not user.is_ns:
                if not user.password:
                    raise AuthError
                await self.register(user, user.password)
            self._api = await self.api_factory.create(user)
        return self._api

    @invalidate_cache(UserCacheKey)
    async def register(self, user: UserDto, raw_password: str, retry: int = 3) -> bool:
        if retry == 0:
            return False
        user.password = encode_ns_password(raw_password)
        try:
            api = await self.api_factory.create(user)
        except AuthError:
            return False
        except NoResponseFromServerError:
            await asyncio.sleep(10)
            return await self.register(user=user, raw_password=raw_password, retry=retry-1)
        user.is_ns = True
        user.default_child = api.current_student if api.current_student else 0
        if api.students and len(api.students) > 1:
            user.is_parent = True
        async with self.uow:
            await self.uow.users.update(user.telegram_id, **user.changed_data)
        return True

    def get_netschool_response_key(
            self, user: UserDto, student_id: Optional[int], *args, **kwargs
    ) -> str:
        assert user.login
        if not student_id:
            student_id = user.default_child
        args = tuple(*args, *kwargs.values())
        key = NetschoolResponseKey(user.login, student_id, get_ns_request_hash(args))
        return self.retort.dump(key)

    @provide_cache(key_builder=get_netschool_response_key, ttl=TTL_10M)
    async def get_day(self, user: UserDto, student_id: Optional[int], day_date: date) -> str:
        api = await self._get_api(user)
        # TODO: сделать выбор другой школы в настройках ЭЖ
        diary = await api.diary(start=day_date, student_id=student_id)

        day = diary.schedule[0]
        if day is None:
            raise DayNotFoundError("День является выходным, или уроки в него еще не добавлены.")

        await self.api_factory.update_session_data(api)
        return await self._parse_day(day, api.current_student)

    @provide_cache(key_builder=get_netschool_response_key, ttl=TTL_10M)
    async def get_duty(self, user: UserDto, student_id: Optional[int] = None) -> str:
        api = await self._get_api(user)
        assignments = await api.overdue(student_id=student_id)

        if assignments is not None:
            return await self._parse_duty(assignments, student_id or api.current_student)

        await self.api_factory.update_session_data(api)
        return self.i18n.get("no-overdue-assignments")

    @provide_cache(key_builder=get_netschool_response_key, ttl=TTL_10M)
    async def get_info(
            self,
            user: UserDto,
            student_id: Optional[int],
            day_date: date,
            lesson_id: int,
            assignment_id: int
    ) -> tuple[dict, dict]:
        api = await self._get_api(user)
        diary = await api.diary(start=day_date, student_id=student_id)
        lesson = self._find_by_key("lesson_id", str(lesson_id), diary.schedule[0].lessons)
        if lesson is None:
            raise LessonNotFoundError()
        assignment = self._find_by_key("id", str(assignment_id), lesson.assignments)
        if assignment is None:
            raise AssignmentNotFoundError()
        info = await api.assignment_info(assignment_id, student_id)

        await self.api_factory.update_session_data(api)
        return assignment.model_dump(), info.model_dump()

    @provide_cache(key_builder=get_netschool_response_key, ttl=TTL_10M)
    async def get_report_filters(self, user: UserDto, student_id: Optional[int]) -> dict:
        api = await self._get_api(user)
        init_data = await api.init_reports()

        return init_data

    @provide_cache(key_builder=get_netschool_response_key, ttl=TTL_10M)
    async def get_report(
            self,
            user: UserDto,
            student_id: Optional[int],
            report_id: str,
            filters: Optional[list[dict[str, str]]]
    ) -> str:
        api = await self._get_api(user)
        report = await api.report(report_id, student_id, filters, requests_timeout=120)

        await self.api_factory.update_session_data(api)
        return report

    @provide_cache(key_builder=get_netschool_response_key, ttl=TTL_10M)
    async def get_diary(
            self, user: UserDto, student_id: Optional[int], start: date, end: date
    ) -> dict:
        api = await self._get_api(user)
        diary = await api.diary(start, end, student_id)

        await self.api_factory.update_session_data(api)
        return diary.model_dump()

    @provide_cache(key_builder=get_netschool_response_key, ttl=TTL_10M)
    async def get_attachment(
            self, user: UserDto, student_id: Optional[int], assignment_id: int, attachment_id: int
    ) -> tuple[BufferedInputFile, str]:
        api = await self._get_api(user)
        attachment = await api.download_attachment(attachment_id, assignment_id, student_id)
        info = await api.assignment_info(assignment_id, student_id)
        attachment_info = self._find_by_key(
            "id", str(attachment_id), info.attachments
        )

        await self.api_factory.update_session_data(api)
        return BufferedInputFile(
            attachment, attachment_info.name if attachment_info else self.i18n.get("without-name")
        ), f"<b>{info.subject.name}</b>\n{info.name}"

    @provide_cache(key_builder=get_netschool_response_key, ttl=TTL_7D)
    async def get_students(self, user: UserDto) -> list[StudentDto]:
        api = await self._get_api(user)
        students = api.students
        convert = self.conversion_retort.get_converter(
            list[Student], list[StudentDto]
        )
        return convert(students)

    #

    async def _parse_day(self, day: Day, student_id: int) -> str:

        message_text = []
        for lesson in day.lessons:
            if lesson.assignments:
                for assignment in lesson.assignments:
                    link = await self.bot_service.get_mini_app_url(
                        "$".join([
                            day.day.strftime("%Y$%m$%d"),
                            str(lesson.lesson_id),
                            str(assignment.id),
                            str(student_id)
                        ]))
                    message_text.append(self.i18n.get(
                        "journal-assignment",
                        is_duty=assignment.is_duty,
                        subject=lesson.subject,
                        type=assignment.type,
                        link=link,
                        content=assignment.content,
                        mark=assignment.mark
                    ))
            else:
                message_text.append(self.i18n.get("journal-no-assignments", subject=lesson.subject))
        return "\n\n".join(message_text)

    async def _parse_duty(
            self, assignments: List[Assignment], student_id: int
    ) -> str:
        bot_username = cast(str, (await self.bot.get_me()).username)
        assert self._api

        message_text = []
        for assignment in assignments:
            info = await self._api.assignment_info(assignment.id, student_id=student_id)
            link = create_telegram_link(bot_username, "journal", startapp=f"{info.id}a{student_id}")
            message_text.append(self.i18n.get(
                "journal-duty",
                assignment_type=info.type,
                subject=info.subject,
                link=link,
                content=info.name
            ))
        return self.i18n.get("journal-overdue")+"\n\n"+"\n\n".join(message_text)

    @staticmethod
    def _find_by_key(
            key_name: str, key: str, data: List[T]
    ) -> Optional[T]:
        for item in data:
            if str(item.__getattribute__(key_name)) == key:
                return item
        return None
