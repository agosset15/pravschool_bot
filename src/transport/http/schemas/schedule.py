from typing import Optional

from pydantic import BaseModel, TypeAdapter, field_validator
from pydantic_core.core_schema import ValidationInfo

from src.core.enums import ScheduleType, WeekDay


class ScheduleOnlyResponse(BaseModel):
    id: int
    grade: str


class ScheduleResponse(BaseModel):
    type: ScheduleType
    grade: str
    days: list["DayResponse"]


class DayResponse(BaseModel):
    id: int
    name: str
    lessons: list["LessonResponse"]

    @field_validator("name")
    @classmethod
    def serialize_type(cls, value: WeekDay, info: ValidationInfo) -> str:
        return info.context["days"][int(value) - 1]  # ty:ignore[not-subscriptable]


class LessonResponse(BaseModel):
    number: int
    name: Optional[str]
    room: Optional[str]
    homework: Optional["HomeworkResponse"]


class HomeworkResponse(BaseModel):
    text: str
    image: str


ListScheduleResponse = TypeAdapter(list[ScheduleResponse])
ListScheduleOnlyResponse = TypeAdapter(list[ScheduleOnlyResponse])
