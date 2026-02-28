from typing import Optional

from sqlalchemy import BigInteger, ForeignKey, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.enums import UserRole

from .base import BaseSql
from .timestamp import TimestampMixin


class User(BaseSql, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, index=True, unique=True)

    username: Mapped[Optional[str]] = mapped_column(String(32), index=True)
    referral_code: Mapped[Optional[str]] = mapped_column(String(64), index=True, unique=True)

    is_blocked: Mapped[bool] = mapped_column(default=False)

    name: Mapped[str] = mapped_column(String(128))
    role: Mapped[UserRole] = mapped_column(index=True)
    grade: Mapped[str] = mapped_column(String(length=50), default="0")

    is_ns: Mapped[bool] = mapped_column(default=False)
    is_teacher: Mapped[bool] = mapped_column(default=False)
    is_parent: Mapped[bool] = mapped_column(default=False)

    default_child: Mapped[int] = mapped_column(default=0)
    login: Mapped[Optional[str]] = mapped_column(String(length=255))
    password: Mapped[Optional[bytes]] = mapped_column(LargeBinary(length=255))

    schedule_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("schedules.id", ondelete="SET NULL", onupdate="SET NULL")
    )