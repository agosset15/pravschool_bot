import datetime
from typing import Any, List, Optional, Self

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_serializer, model_validator

__all__ = [
    "NetSchoolAPISchema",
    "Attachment",
    "Announcement",
    "Assignment",
    "Diary",
    "School",
    "Day",
    "AssignmentInfo",
    "ShortSchool",
    "Student"
]


class NetSchoolAPISchema(BaseModel):
    model_config = ConfigDict(validate_assignment=False)


class Attachment(NetSchoolAPISchema):
    id: int
    name: str = Field(alias="originalFileName")
    description: str = Field(default="")


class Author(NetSchoolAPISchema):
    id: int
    full_name: str = Field(alias="fio")
    nickname: str = Field(alias="nickName")


class Announcement(NetSchoolAPISchema):
    name: str
    author: Author
    content: str = Field(alias="description")
    post_date: datetime.datetime = Field(alias="postDate")
    attachments: List[Attachment] = Field(default_factory=list)


class Assignment(NetSchoolAPISchema):
    id: int
    wrapped_comment: Optional[dict[str, str]] = Field(default_factory=dict, alias="markComment", exclude=True)
    comment: str = ""
    type_id: int = Field(alias="typeId", exclude=True)
    type: Optional[str] = None
    subject: str = Field(alias="subjectName", default="")
    content: str = Field(alias="assignmentName")
    mark: Optional[Any] = None
    is_duty: bool = Field(alias="dutyMark", default=False)
    deadline: datetime.date = Field(alias="dueDate")
    lesson_id: int = Field(alias="classMeetingId")

    @field_serializer("deadline")
    def serialize_deadline(self, deadline: datetime.date, _info):
        return deadline.strftime("%d/%m")

    @model_validator(mode="after")
    def unwrap_marks(self, info: ValidationInfo) -> Self:
        if self.mark:
            wrapped_mark = dict(**self.mark)
            self.mark = int(wrapped_mark["mark"]) if wrapped_mark["mark"] else None
            self.is_duty = bool(wrapped_mark["dutyMark"]) if wrapped_mark["dutyMark"] else False
        else:
            self.mark = None
            self.is_duty = False
        if self.wrapped_comment:
            self.comment = self.wrapped_comment["name"]
        self.type = info.context["assignment_types"][self.type_id]  # ty:ignore[not-subscriptable]
        return self


class Teacher(NetSchoolAPISchema):
    id: int
    name: str


class Subject(NetSchoolAPISchema):
    id: int
    name: str
    grade: Optional[str] = None

    @model_validator(mode="after")
    def unwrap_subject(self) -> Self:
        name = self.name.split("/")
        if len(name) > 1:
            self.grade = name.pop(0)
            self.name = name.pop(0)
        else:
            self.name = name[0]
        return self


class AssignmentInfo(NetSchoolAPISchema):
    id: int
    type_id: Optional[int] = Field(alias="typeId", exclude=True, default=None)
    type: Optional[str] = None
    name: str = Field(alias="assignmentName")
    subject: Subject = Field(alias="subjectGroup", default_factory=dict)
    teachers: List[Teacher]
    weight: int
    date: datetime.date
    description: Optional[str] = None
    attachments: List[Attachment] = Field(default_factory=list)

    @field_serializer("teachers")
    def serialize_teachers(self, teachers: List[Teacher], _info):
        return [x.name for x in teachers]

    @field_serializer("date")
    def serialize_date(self, date: datetime.date, _info):
        return date.strftime("%d/%m")

    @field_serializer("subject")
    def serialize_subject(self, subject: Subject, _info):
        return subject.name

    @model_validator(mode="after")
    def unwrap_type(self, info: ValidationInfo) -> Self:
        if self.type_id:
            self.type = info.context["assignment_types"][self.type_id]  # ty:ignore[not-subscriptable]
        return self


class Lesson(NetSchoolAPISchema):
    day: datetime.date
    lesson_id: int = Field(alias="classmeetingId")
    start: datetime.time = Field(alias="startTime")
    end: datetime.time = Field(alias="endTime")
    room: Optional[str] = None
    number: int
    subject: str = Field(alias="subjectName")
    assignments: List[Assignment] = Field(default_factory=list)


class Day(NetSchoolAPISchema):
    lessons: List[Lesson]
    day: datetime.date = Field(alias="date")


class Diary(NetSchoolAPISchema):
    start: datetime.date = Field(alias="weekStart")
    end: datetime.date = Field(alias="weekEnd")
    schedule: List[Day] = Field(alias="weekDays")
    class_name: Optional[str] = Field(alias="className", default=None)
    term_name: Optional[str] = Field(alias="termName", default=None)


class ShortSchool(NetSchoolAPISchema):
    name: str
    id: int
    address: str = Field(alias="addressString")


class School(NetSchoolAPISchema):
    name: str = Field(alias="fullSchoolName")
    about: str

    address: str
    email: str
    site: str = Field(alias="web")
    phone: str = Field(alias="phones")

    director: str
    AHC: str = Field(alias="principalAHC")
    IT: str = Field(alias="principalIT")
    UVR: str = Field(alias="principalUVR")

    @classmethod
    @model_validator(mode="before")
    def unwrap_nested_dicts(cls, school: Any) -> Any:
        school.update(school.pop("commonInfo"))
        school.update(school.pop("contactInfo"))
        school.update(school.pop("managementInfo"))
        school["address"] = school["juridicalAddress"] or school["postAddress"]
        return school

class Student(NetSchoolAPISchema):
    id: int = Field(alias="studentId")
    name: str = Field(alias="nickName")
    class_name: Optional[str] = None
    class_id: Optional[int] = None