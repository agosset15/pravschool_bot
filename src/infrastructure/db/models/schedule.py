from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.enums import ScheduleType, WeekDay

from .base import BaseSql
from .timestamp import TimestampMixin


class SchedulesExtra(BaseSql):
    __tablename__ = "schedules_extra"

    id: Mapped[int] = mapped_column(primary_key=True)
    year_photo_id: Mapped[Optional[str]] = mapped_column(String(length=255), nullable=True)


class Schedule(BaseSql):
    __tablename__ = "schedules"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[ScheduleType] = mapped_column(index=True)
    grade: Mapped[str] = mapped_column(String(length=50))
    days: Mapped[list["Day"]] = relationship(lazy="selectin", order_by="Day.id")


class Day(BaseSql):
    __tablename__ = "days"

    id: Mapped[int] = mapped_column(primary_key=True)
    schedule_id: Mapped[int] = mapped_column(ForeignKey("schedules.id", ondelete="CASCADE"), index=True)
    name: Mapped[WeekDay]
    lessons: Mapped[list["Lesson"]] = relationship(lazy="joined", order_by="Lesson.number")


class Lesson(BaseSql):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(primary_key=True)
    day_id: Mapped[int] = mapped_column(ForeignKey("days.id", ondelete="CASCADE"), index=True)
    number: Mapped[int]
    name: Mapped[Optional[str]] = mapped_column(String(length=255))
    room: Mapped[Optional[str]] = mapped_column(String(length=50))
    homework: Mapped["Homework"] = relationship(lazy="selectin")


class Homework(BaseSql, TimestampMixin):
    __tablename__ = "homeworks"

    id: Mapped[int] = mapped_column(primary_key=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"), index=True)
    text: Mapped[str] = mapped_column(String(length=255))
    image: Mapped[str] = mapped_column(String(length=255)) # TODO: save images to media location and serve to web