from dataclasses import dataclass

from src.core.enums import ScheduleType

from .key_builder import StorageKey

USER_LIST_PREFIX = "user_list"
USER_COUNT_PREFIX = "user_count"
SCHEDULES_EXTRA_PREFIX = "schedules_extra"


@dataclass(frozen=True)
class UserCacheKey(StorageKey, prefix="user"):
    telegram_id: int


@dataclass(frozen=True)
class WebhookLockKey(StorageKey, prefix="webhook_lock"):
    bot_id: int
    webhook_hash: str


@dataclass(frozen=True)
class ScheduleCacheKey(StorageKey, prefix="schedule"):
    schedule_id: int


@dataclass(frozen=True)
class SchedulesSearchKey(StorageKey, prefix="schedules_search"):
    schedule_type: ScheduleType
    grade: str


@dataclass(frozen=True)
class SchedulesListCacheKey(StorageKey, prefix="schedules_list"):
    schedule_type: ScheduleType
    with_days: bool = False


@dataclass(frozen=True)
class NetschoolSessionDataKey(StorageKey, prefix="ns_cookies"):
    login: str


@dataclass(frozen=True)
class NetschoolResponseKey(StorageKey):
    login: str
    student_id: int
    request_hash: str


@dataclass(frozen=True)
class NetschoolStudentsKey(StorageKey, prefix="ns_students"):
    login: str
