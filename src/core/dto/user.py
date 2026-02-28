from dataclasses import dataclass
from typing import Optional, Self

from aiogram import html
from aiogram.types import User as AiogramUser
from aiogram.utils.link import create_tg_link

from src.core.enums import UserRole
from src.core.utils.time import datetime_now

from .base import BaseDto, TimestampMixin, TrackableMixin


@dataclass(kw_only=True)
class TempUserDto:
    telegram_id: int
    name: str

    @classmethod
    def from_aiogram(cls, aiogram_user: AiogramUser) -> Self:
        return cls(
            telegram_id=aiogram_user.id,
            name=aiogram_user.full_name,
        )


@dataclass(kw_only=True)
class UserDto(BaseDto, TrackableMixin, TimestampMixin):
    telegram_id: int

    username: Optional[str] = None
    referral_code: Optional[str] = None

    is_blocked: bool = False

    name: str
    role: UserRole = UserRole.USER
    grade: str = "0"

    is_ns: bool = False
    is_teacher: bool = False
    is_parent: bool = False

    default_child: int = 0
    login: Optional[str] = None
    password: Optional[bytes] = None

    schedule_id: Optional[int] = None

    @property
    def url(self) -> str:
        return create_tg_link("user", id=self.telegram_id)

    @property
    def mention(self) -> str:
        return html.link(value=self.name, link=self.url)

    @property
    def text(self):
        return " ".join([
            self.mention,
            self.grade,
            html.italic(self.referral_code if self.referral_code else "")
        ])

    @property
    def age_days(self) -> Optional[int]:
        if self.created_at is None:
            return None

        return (datetime_now() - self.created_at).days

    @property
    def log(self) -> str:
        return f"[{self.telegram_id} ({self.name})]"