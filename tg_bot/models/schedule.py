from typing import List

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from tg_bot.models.db import Base, TimeStampMixin, Int16


class Schedule(Base):
    id: Mapped[Int16] = mapped_column(primary_key=True, autoincrement=True, unique=True)
    entity: Mapped[Int16] = mapped_column(nullable=False)
    grade: Mapped[str] = mapped_column(String(length=50), primary_key=True, nullable=False)
    days: Mapped[List["Day"]] = relationship(lazy="selectin", order_by="Day.id")


class Day(Base):
    id: Mapped[Int16] = mapped_column(primary_key=True, autoincrement=True)
    schedule_id: Mapped[Int16] = mapped_column(ForeignKey("schedules.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(length=100), nullable=False)
    lessons: Mapped[List["Lesson"]] = relationship(lazy="joined", order_by="Lesson.number")

    @property
    def lessons_text(self):
        lessons = []
        for i, lesson in enumerate(self.lessons):
            if i > 0:
                if lesson.number == self.lessons[i - 1].number and lesson.name == self.lessons[i - 1].name:
                    lessons[-1] = self.lessons[i - 1].text[:-1] + '/' + lesson.room + ')'
                    continue
                elif lesson.number == self.lessons[i - 1].number:
                    lessons[-1] = self.lessons[i - 1].text + '//' + lesson.text[3:]
                    continue
            lessons.append(lesson.text)
        return lessons

    @property
    def text(self):
        return '\n'.join(self.lessons_text)

    def separated_text(self, separator: str = '\n'):
        return separator.join(self.lessons_text)


class Lesson(Base):
    id: Mapped[Int16] = mapped_column(primary_key=True, autoincrement=True)
    day_id: Mapped[Int16] = mapped_column(ForeignKey("days.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    number: Mapped[Int16] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(String(length=255), nullable=True)
    room: Mapped[str] = mapped_column(String(length=50), nullable=True)
    homework: Mapped["Homework"] = relationship(lazy="selectin")

    @property
    def text(self):
        if self.name:
            return f"{self.number}. {self.name}"+(f"({self.room})" if self.room else '')
        return f"{self.number}. "


class Homework(Base, TimeStampMixin):
    id: Mapped[Int16] = mapped_column(primary_key=True, autoincrement=True)
    lesson_id: Mapped[Int16] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    homework: Mapped[str] = mapped_column(String(length=255))
    image: Mapped[str] = mapped_column(String(length=255))
