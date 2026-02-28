from enum import Enum, IntEnum, StrEnum, auto
from typing import Optional

from aiogram.types import BotCommand
from fluentogram import TranslatorRunner


class UpperStrEnum(StrEnum):
    @staticmethod
    def _generate_next_value_(name: str, start: int, count: int, last_values: list) -> str:
        return name

class ScheduleType(UpperStrEnum):
    COMMON = auto()
    TEACHER = auto()
    ROOM = auto()

class WeekDay(IntEnum):
    MONDAY = auto()
    TUESDAY = auto()
    WEDNESDAY = auto()
    THURSDAY = auto()
    FRIDAY = auto()
    SATURDAY = auto()
    SUNDAY = auto()

    def __str__(self):
        return self.name.lower()

    def get_text(self, i18n: TranslatorRunner):
        return i18n.get(f"days.{self.name.lower()}")

    @classmethod
    def str_list(cls, i18n: TranslatorRunner) -> list[str]:
        return [i18n.get(f"days.{day.name.lower()}") for day in cls]

    @classmethod
    def names(cls) -> list[str]:
        return [day.name.lower() for day in cls]

class Month(IntEnum):
    JANUARY = auto()
    FEBRUARY = auto()
    MARCH = auto()
    APRIL = auto()
    MAY = auto()
    JUNE = auto()
    JULY = auto()
    AUGUST = auto()
    SEPTEMBER = auto()
    OCTOBER = auto()
    NOVEMBER = auto()
    DECEMBER = auto()

    def get_text(self, i18n: TranslatorRunner):
        return i18n.get(f"months.{self.name.lower()}")

    def get_text_possessive(self, i18n: TranslatorRunner):
        return i18n.get(f"months-possessive.{self.name.lower()}")

    @classmethod
    def str_list(cls, i18n: TranslatorRunner) -> list[str]:
        return [i18n.get(f"days.{day.name.lower()}") for day in cls]

class Command(Enum):
    START = BotCommand(command="start", description="command.start")
    OVERDUE = BotCommand(command="overdue", description="command.overdue")
    HELP = BotCommand(command="help", description="command.help")

class LogLevel(UpperStrEnum):
    CRITICAL = auto()
    FATAL = auto()
    ERROR = auto()
    WARN = auto()
    WARNING = auto()
    INFO = auto()
    DEBUG = auto()
    NOTSET = auto()

class BroadcastStatus(UpperStrEnum):
    PROCESSING = auto()
    COMPLETED = auto()
    CANCELED = auto()
    DELETED = auto()
    ERROR = auto()


class BroadcastMessageStatus(UpperStrEnum):
    SENT = auto()
    FAILED = auto()
    EDITED = auto()
    DELETED = auto()
    PENDING = auto()


class BroadcastAudience(UpperStrEnum):
    ALL = auto()
    PARENTS = auto()
    TEACHERS = auto()
    NS = auto()
    ADMINS = auto()


class UserRole(IntEnum):
    USER = auto()
    ADMIN = auto()
    DEV = auto()

    def __str__(self) -> str:
        return self.name

    def includes(self, other: "UserRole") -> bool:
        return self >= other

class MessageEffectId(StrEnum):
    THUMBS_UP = "5107584321108051014" # 👍 Thumbs Up
    THUMBS_DOWN = "5104858069142078462" # 👎 Thumbs Down
    HEART = "5159385139981059251" # ❤️ Heart
    FIRE = "5104841245755180586" # 🔥 Fire
    PARTY = "5046509860389126442" # 🎉 Party Popper
    POOP = "5046589136895476101" # 💩 Pile of Poo

class MediaType(UpperStrEnum):
    PHOTO = auto()
    VIDEO = auto()
    DOCUMENT = auto()

class SystemNotificationType(UpperStrEnum):
    ERROR = auto()
    TASK_SUCCEED = auto()
    #
    BOT_LIFECYCLE = auto()
    #
    USER_REGISTERED = auto()

    def get_logs_topic(self, topic_id_list: list[int]) -> Optional[int]:
        match self:
            case SystemNotificationType.BOT_LIFECYCLE:
                return topic_id_list[0]
            case SystemNotificationType.USER_REGISTERED:
                return topic_id_list[1]
        return None

class UserNotificationType(UpperStrEnum):
    TOMORROW_SCHEDULE = auto()
    OVERDUE = auto()
    #
    NS_ERROR = auto()
    NS_TimeoutReached = auto()


class Locale(StrEnum):
    EN = auto()  # English
    RU = auto()  # Russian

# https://docs.aiogram.dev/en/latest/api/types/update.html
class MiddlewareEventType(StrEnum):
    AIOGD_UPDATE = auto()  # AIOGRAM DIALOGS
    UPDATE = auto()
    MESSAGE = auto()
    EDITED_MESSAGE = auto()
    CHANNEL_POST = auto()
    EDITED_CHANNEL_POST = auto()
    BUSINESS_CONNECTION = auto()
    BUSINESS_MESSAGE = auto()
    EDITED_BUSINESS_MESSAGE = auto()
    DELETED_BUSINESS_MESSAGES = auto()
    MESSAGE_REACTION = auto()
    MESSAGE_REACTION_COUNT = auto()
    INLINE_QUERY = auto()
    CHOSEN_INLINE_RESULT = auto()
    CALLBACK_QUERY = auto()
    SHIPPING_QUERY = auto()
    PRE_CHECKOUT_QUERY = auto()
    PURCHASED_PAID_MEDIA = auto()
    POLL = auto()
    POLL_ANSWER = auto()
    MY_CHAT_MEMBER = auto()
    CHAT_MEMBER = auto()
    CHAT_JOIN_REQUEST = auto()
    CHAT_BOOST = auto()
    REMOVED_CHAT_BOOST = auto()
    ERROR = auto()

class InlineQueryText(StrEnum):
    ROOMS = "#room"
    GRADES = "#rade"
    TEACHERS = "#teacher"
