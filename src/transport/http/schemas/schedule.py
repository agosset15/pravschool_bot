from typing import Optional

from pydantic import BaseModel, field_serializer

from src.core.enums import ScheduleType, WeekDay


class ScheduleResponse(BaseModel):
    type: ScheduleType
    grade: str
    days: list["DayResponse"]

class DayResponse(BaseModel):
    name: WeekDay
    lessons: list["LessonResponse"]

    @field_serializer("name")
    def serialize_type(self, value: ScheduleType) -> str:
        return str(value)

class LessonResponse(BaseModel):
    number: int
    name: Optional[str]
    room: Optional[str]
    homework: Optional["HomeworkResponse"]

class HomeworkResponse(BaseModel):
    text: str
    image: str
