from aiogram import html
from aiogram.utils.link import create_tg_link
from sqlalchemy import Integer, String, ForeignKey, LargeBinary, Identity
from sqlalchemy.orm import Mapped, mapped_column

from tg_bot.models.db import TimeStampMixin, Base, ChatIdMixin, Int64, Int16
from .schedule import Schedule


class User(Base, TimeStampMixin, ChatIdMixin):
    id: Mapped[Int64] = mapped_column(Integer, Identity(always=True, start=1, cycle=True),
                                      primary_key=True)
    is_admin: Mapped[bool] = mapped_column(default=False)
    is_ns: Mapped[bool] = mapped_column(default=False)
    is_teacher: Mapped[bool] = mapped_column(default=False)
    is_parent: Mapped[bool] = mapped_column(default=False)
    default_child: Mapped[Int16] = mapped_column(default=0, nullable=True)
    login: Mapped[str] = mapped_column(String(length=255), nullable=True)
    password: Mapped[bytes] = mapped_column(LargeBinary(length=255), nullable=True)
    grade: Mapped[str] = mapped_column(String(length=50), default='0', nullable=True)
    blocked: Mapped[bool] = mapped_column(default=False)
    ref: Mapped[str] = mapped_column(String(length=255), nullable=True)
    schedule: Mapped[Int16] = mapped_column(ForeignKey(Schedule.id, ondelete="SET NULL", onupdate="SET NULL"),
                                            nullable=True)

    @property
    def url(self) -> str:
        return create_tg_link("user", id=self.chat_id)

    @property
    def mention(self) -> str:
        return html.link(value=self.name, link=self.url)

    @property
    def text(self):
        return f"{self.mention} {self.grade} {html.italic(self.ref if self.ref else '')}"
