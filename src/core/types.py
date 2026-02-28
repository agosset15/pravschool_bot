from typing import TYPE_CHECKING, Annotated, NewType, TypeAlias, Union

from aiogram.types import (
    ForceReply,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from pydantic import PlainValidator

from .constants import COMMA
from .enums import Locale, SystemNotificationType, UserNotificationType

if TYPE_CHECKING:
    ListStr: TypeAlias = list[str]
    ListLocale: TypeAlias = list[Locale]
else:
    ListStr = NewType("ListStr", list[str])
    ListLocale = NewType("ListLocale", list[Locale])

StringList: TypeAlias = Annotated[
    ListStr, PlainValidator(lambda x: [s.strip() for s in x.split(COMMA)])
]

LocaleList: TypeAlias = Annotated[
    ListLocale,
    PlainValidator(
        func=lambda x: [Locale(loc.strip()) for loc in (x if isinstance(x, list) else x.split(COMMA))]
    ),
]

AnyKeyboard: TypeAlias = Union[
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    ForceReply,
]

NotificationType: TypeAlias = Union[SystemNotificationType, UserNotificationType]