from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from src.core.constants import LESSON_TIMES  # noqa: F401
from src.core.enums import ScheduleType, WeekDay

from .base import BaseDto, TimestampMixin, TrackableMixin


@dataclass(kw_only=True)
class SchedulesExtraDto(BaseDto, TrackableMixin):
    year_photo_id: Optional[str] = None


@dataclass(kw_only=True)
class ScheduleDto(BaseDto, TrackableMixin):
    type: ScheduleType
    grade: str
    days: list["DayDto"] = field(default_factory=list)

    @property
    def text(self) -> str:
        return "\n\n".join([
            f"<b>{day.name}</b>:\n" + day.text for day in self.days
        ])

    @property
    def list_days(self) -> list[WeekDay]:
        return [day.name for day in self.days]


@dataclass(kw_only=True)
class DayDto(BaseDto):
    name: WeekDay
    lessons: list["LessonDto"] = field(default_factory=list)

    @property
    def lessons_text(self) -> list[str]:
        lessons: list[str] = []
        for i, lesson in enumerate(self.lessons):
            if i > 0:
                prev_lesson = self.lessons[i - 1]
                if (lesson.number == prev_lesson.number) and (lesson.name == prev_lesson.name):
                    lessons[-1] = lesson.text_split_room(prev_lesson.room)
                    continue
                elif lesson.number == prev_lesson.number:
                    lessons[-1] = prev_lesson.text + "//" + lesson.text[3:]
                    continue
            lessons.append(lesson.text)
        return lessons

    @property
    def lessons_list(self) -> list[str]:
        lessons: list[str] = []
        for i, lesson in enumerate(self.lessons):
            if i > 0:
                prev_lesson = self.lessons[i - 1]
                if (lesson.number == prev_lesson.number) and (lesson.name == prev_lesson.name):
                    continue
                elif lesson.number == prev_lesson.number:
                    lessons[-1] = f"{prev_lesson.name}//{lesson.name}"
                    continue
            lessons.append(lesson.name)
        return lessons

    @property
    def text(self) -> str:
        return "\n".join(self.lessons_text)


@dataclass(kw_only=True)
class LessonDto(BaseDto):
    number: int
    name: Optional[str]
    room: Optional[str]
    homework: Optional["HomeworkDto"] = field(default_factory=list)

    @property
    def text(self) -> str:
        if self.name:
            return f"{self.number}. {self.name}"+(f"({self.room})" if self.room else "")
        return f"{self.number}. "

    def text_split_room(self, room: Optional[str]) -> str:
        if self.room == room or self.room is None:
            return self.text
        if self.name:
            return f"{self.number}. {self.name}"+(f"({self.room} / {room})" if self.room else "")
        return f"{self.number}. "


@dataclass(kw_only=True)
class HomeworkDto(BaseDto, TimestampMixin):
    text: str
    image: str
    updated_at: datetime
