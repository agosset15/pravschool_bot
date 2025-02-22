from __future__ import annotations
from dataclasses import field, dataclass
import datetime
from loguru import logger
from typing import Any, Dict, List

from marshmallow import EXCLUDE, Schema, pre_load
from marshmallow_dataclass import class_schema

__all__ = ['Attachment', 'Announcement', 'Assignment', 'Diary', 'School', 'Day']


class NetSchoolAPISchema(Schema):
    class Meta:
        dateformat = '%Y-%m-%dT00:00:00'
        unknown = EXCLUDE


@dataclass()
class Attachment(NetSchoolAPISchema):
    id: int
    name: str = field(metadata=dict(data_key='originalFileName'))
    description: str = field(metadata=dict(
        allow_none=True, missing='', required=False
    ))

    @property
    def json(self):
        return {'id': self.id, 'name': self.name, 'description': self.description}


@dataclass()
class Author(NetSchoolAPISchema):
    id: int
    full_name: str = field(metadata=dict(data_key="fio"))
    nickname: str = field(metadata=dict(data_key="nickName"))


@dataclass()
class Announcement(NetSchoolAPISchema):
    name: str
    author: Author
    content: str = field(metadata=dict(data_key='description'))
    post_date: datetime.datetime = field(metadata=dict(data_key='postDate'))
    attachments: List[Attachment] = field(default_factory=list)


@dataclass()
class Assignment(NetSchoolAPISchema):
    id: int
    comment: str
    type: str
    subject: str = field(metadata=dict(data_key='subjectName', allow_none=True, missing='', required=False))
    content: str = field(metadata=dict(data_key='assignmentName'))
    mark: int = field(metadata=dict(allow_none=True, data_key='mark'))
    is_duty: bool = field(metadata=dict(data_key='dutyMark'))
    deadline: datetime.date = field(metadata=dict(data_key='dueDate'))
    lesson_id: int = field(metadata=dict(data_key='classMeetingId'))

    @property
    def json(self):
        return {'id': self.id, 'comment': self.comment, '_type': self.type, 'content': self.content, 'mark': self.mark,
                'is_duty': self.is_duty, 'deadline': self.deadline.strftime('%d/%m'), 'lesson_id': self.lesson_id}

    @pre_load
    def unwrap_marks(self, assignment: Dict[str, Any], **_) -> Dict[str, str]:
        mark = assignment.pop('mark', None)
        if mark:
            assignment.update(mark)
        else:
            assignment.update({'mark': None, 'dutyMark': False})
        mark_comment = assignment.pop("markComment", None)
        assignment["comment"] = mark_comment["name"] if mark_comment else ""
        assignment["type"] = self.context["assignment_types"][assignment.pop("typeId")]
        return assignment


@dataclass()
class Teacher(NetSchoolAPISchema):
    id: int
    name: str


@dataclass()
class Subject(NetSchoolAPISchema):
    id: int
    name: str
    grade: str

    @pre_load
    def unwrap_subject(self, subject: Dict[str, Any], **_) -> Dict[str, str]:
        name = subject.pop('name', '').split('/')
        if len(name) > 1:
            subject.update({'grade': name.pop(0), 'name': name.pop(0)})
        else:
            subject.update({'name': name[0]})
        return subject


@dataclass()
class AssignmentInfo(NetSchoolAPISchema):
    id: int
    type: str = field(metadata=dict(allow_none=True))
    name: str = field(metadata=dict(data_key='assignmentName'))
    subject: Subject = field(metadata=dict(data_key='subjectGroup', default_factory=dict))
    teachers: List[Teacher]
    weight: int = field(metadata=dict(data_key='weight'))
    date: datetime.date = field(metadata=dict(data_key='date'))
    description: str = field(metadata=dict(data_key='description', missing='', allow_none=True, required=False))
    attachments: List[Attachment] = field(
        metadata=dict(data_key='attachments', default_factory=list))

    @property
    def json(self):
        return {'id': self.id, 'name': self.name, 'subject': self.subject.name,
                'teachers': [x.name for x in self.teachers], 'weight': self.weight, 'description': self.description,
                'attachments': [x.json for x in self.attachments]}

    @pre_load
    def unwrap_type(self, assignment_info: Dict[str, Any], **_) -> Dict[str, Any]:
        if "typeId" in assignment_info.keys():
            assignment_info["type"] = self.context["assignment_types"][assignment_info.pop("typeId")]
        else:
            assignment_info["type"] = None
        return assignment_info


@dataclass()
class Lesson(NetSchoolAPISchema):
    day: datetime.date
    lesson_id: int = field(metadata=dict(data_key='classmeetingId'))
    start: datetime.time = field(metadata=dict(data_key='startTime'))
    end: datetime.time = field(metadata=dict(data_key='endTime'))
    room: str = field(metadata=dict(
        missing='', allow_none=True, required=False
    ))
    number: int
    subject: str = field(metadata=dict(data_key='subjectName'))
    assignments: List[Assignment] = field(default_factory=list)


@dataclass()
class Day(NetSchoolAPISchema):
    lessons: List[Lesson]
    day: datetime.date = field(metadata=dict(data_key='date'))


@dataclass()
class Diary(NetSchoolAPISchema):
    start: datetime.date = field(metadata=dict(data_key='weekStart'))
    end: datetime.date = field(metadata=dict(data_key='weekEnd'))
    schedule: List[Day] = field(metadata=dict(data_key='weekDays'))


@dataclass()
class ShortSchool(NetSchoolAPISchema):
    name: str
    id: int
    address: str = field(metadata=dict(data_key="addressString"))


@dataclass()
class School(NetSchoolAPISchema):
    name: str = field(metadata=dict(data_key='fullSchoolName'))
    about: str

    address: str
    email: str
    site: str = field(metadata=dict(data_key='web'))
    phone: str = field(metadata=dict(data_key='phones'))

    director: str
    AHC: str = field(metadata=dict(data_key='principalAHC'))
    IT: str = field(metadata=dict(data_key='principalIT'))
    UVR: str = field(metadata=dict(data_key='principalUVR'))

    @pre_load
    def unwrap_nested_dicts(
            self, school: Dict[str, Any], **_) -> Dict[str, str]:
        school.update(school.pop('commonInfo'))
        school.update(school.pop('contactInfo'))
        school.update(school.pop('managementInfo'))
        school['address'] = school['juridicalAddress'] or school['postAddress']
        return school


with logger.catch():
    AttachmentSchema = class_schema(Attachment, localns={})
DiarySchema = class_schema(Diary, localns={})
AssignmentInfoSchema = class_schema(AssignmentInfo, localns={})
AssignmentSchema = class_schema(Assignment, localns={})
ShortSchoolSchema = class_schema(ShortSchool, localns={})
SchoolSchema = class_schema(School, localns={})
AnnouncementSchema = class_schema(Announcement, localns={})
