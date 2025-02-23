import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_serializer, model_validator, ValidationInfo, ConfigDict

__all__ = ['Attachment', 'Announcement', 'Assignment', 'Diary', 'School', 'Day']


class NetSchoolAPISchema(BaseModel):
    model_config = ConfigDict(validate_assignment=True)


class Attachment(NetSchoolAPISchema):
    id: int
    name: str = Field(alias='originalFileName')
    description: str = Field(default='')


class Author(NetSchoolAPISchema):
    id: int
    full_name: str = Field(alias="fio")
    nickname: str = Field(alias="nickName")


class Announcement(NetSchoolAPISchema):
    name: str
    author: Author
    content: str = Field(alias='description')
    post_date: datetime.datetime = Field(alias='postDate')
    attachments: List[Attachment] = Field(default_factory=list)


class Assignment(NetSchoolAPISchema):
    id: int
    comment: Optional[str] = None
    type: str
    subject: str = Field(alias='subjectName', default='')
    content: str = Field(alias='assignmentName')
    mark: int = Field(alias='mark')
    is_duty: bool = Field(alias='dutyMark')
    deadline: datetime.date = Field(alias='dueDate')
    lesson_id: int = Field(alias='classMeetingId')

    @field_serializer('deadline')
    def serialize_deadline(self, deadline: datetime.date, _info):
        return deadline.strftime('%d/%m')

    @classmethod
    @model_validator(mode='before')
    def unwrap_marks(cls, data: Dict[str, Any], info: ValidationInfo) -> Dict[str, str]:
        mark = data.pop('mark', None)
        if mark:
            data.update(mark)
        else:
            data.update({'mark': None, 'dutyMark': False})
        mark_comment = data.pop("markComment", None)
        data["comment"] = mark_comment["name"] if mark_comment else ""
        data["type"] = info.context["assignment_types"][data.pop("typeId")]
        return data


class Teacher(NetSchoolAPISchema):
    id: int
    name: str


class Subject(NetSchoolAPISchema):
    id: int
    name: str
    grade: str

    @classmethod
    @model_validator(mode='before')
    def unwrap_subject(cls, data: Dict[str, Any]) -> Dict[str, str]:
        name = data.pop('name', '').split('/')
        if len(name) > 1:
            data.update({'grade': name.pop(0), 'name': name.pop(0)})
        else:
            data.update({'name': name[0]})
        return data


class AssignmentInfo(NetSchoolAPISchema):
    id: int
    type: Optional[str] = None
    name: str = Field(alias='assignmentName')
    subject: Subject = Field(alias='subjectGroup', default_factory=dict)
    teachers: List[Teacher]
    weight: int
    date: datetime.date
    description: Optional[str] = None
    attachments: List[Attachment] = Field(default_factory=list)

    @field_serializer('teachers')
    def serialize_teachers(self, teachers: List[Teacher], _info):
        return [x.name for x in teachers]

    @classmethod
    @model_validator(mode='before')
    def unwrap_type(cls, assignment_info: Dict[str, Any], info: ValidationInfo) -> Dict[str, Any]:
        if "typeId" in assignment_info.keys():
            assignment_info["type"] = info.context["assignment_types"][assignment_info.pop("typeId")]
        else:
            assignment_info["type"] = None
        return assignment_info


class Lesson(NetSchoolAPISchema):
    day: datetime.date
    lesson_id: int = Field(alias='classmeetingId')
    start: datetime.time = Field(alias='startTime')
    end: datetime.time = Field(alias='endTime')
    room: Optional[str] = None
    number: int
    subject: str = Field(alias='subjectName')
    assignments: List[Assignment] = Field(default_factory=list)


class Day(NetSchoolAPISchema):
    lessons: List[Lesson]
    day: datetime.date = Field(alias='date')


class Diary(NetSchoolAPISchema):
    start: datetime.date = Field(alias='weekStart')
    end: datetime.date = Field(alias='weekEnd')
    schedule: List[Day] = Field(alias='weekDays')


class ShortSchool(NetSchoolAPISchema):
    name: str
    id: int
    address: str = Field(alias="addressString")


class School(NetSchoolAPISchema):
    name: str = Field(alias='fullSchoolName')
    about: str

    address: str
    email: str
    site: str = Field(alias='web')
    phone: str = Field(alias='phones')

    director: str
    AHC: str = Field(alias='principalAHC')
    IT: str = Field(alias='principalIT')
    UVR: str = Field(alias='principalUVR')

    @classmethod
    @model_validator(mode='before')
    def unwrap_nested_dicts(cls, school: Dict[str, Any]) -> Dict[str, str]:
        school.update(school.pop('commonInfo'))
        school.update(school.pop('contactInfo'))
        school.update(school.pop('managementInfo'))
        school['address'] = school['juridicalAddress'] or school['postAddress']
        return school
