from dataclasses import dataclass, field
from datetime import date, datetime, time
from typing import List, Optional


@dataclass(kw_only=True)
class NetSchoolAPIDto:
    ...

@dataclass(kw_only=True)
class Attachment(NetSchoolAPIDto):
    id: int
    name: str  # alias: originalFileName
    description: str = ""

@dataclass(kw_only=True)
class Author(NetSchoolAPIDto):
    id: int
    full_name: str  # alias: fio
    nickname: str  # alias: nickName

@dataclass(kw_only=True)
class StudentDto:
    id: int
    class_name: str
    class_id: int
    name: str

@dataclass(kw_only=True)
class Announcement(NetSchoolAPIDto):
    name: str
    author: Author
    content: str  # alias: description
    post_date: datetime  # alias: postDate
    attachments: List[Attachment] = field(default_factory=list)

@dataclass(kw_only=True)
class Assignment(NetSchoolAPIDto):
    id: int
    content: str  # alias: assignmentName
    deadline: date  # alias: dueDate
    lesson_id: int  # alias: classMeetingId
    comment: str = ""
    type_id: int = 0  # alias: typeId
    type: Optional[str] = None
    subject: str = ""  # alias: subjectName
    mark: Optional[int] = None  # В JSON приходит как dict, превращаем в int
    is_duty: bool = False  # alias: dutyMark

@dataclass(kw_only=True)
class Teacher(NetSchoolAPIDto):
    id: int
    name: str

@dataclass(kw_only=True)
class Subject(NetSchoolAPIDto):
    id: int
    name: str
    grade: Optional[str] = None

@dataclass(kw_only=True)
class AssignmentInfo(NetSchoolAPIDto):
    id: int
    name: str  # alias: assignmentName
    weight: int
    date: date
    type_id: Optional[int] = None  # alias: typeId
    type: Optional[str] = None
    subject: Optional[Subject] = field(default=None)  # alias: subjectGroup
    teachers: List[Teacher] = field(default_factory=list)
    description: Optional[str] = None
    attachments: List[Attachment] = field(default_factory=list)

@dataclass(kw_only=True)
class Lesson(NetSchoolAPIDto):
    id: int  # alias: classmeetingId
    day: date
    start: time  # alias: startTime
    end: time  # alias: endTime
    number: int
    subject: str  # alias: subjectName
    room: Optional[str] = None
    assignments: List[Assignment] = field(default_factory=list)

@dataclass(kw_only=True)
class Day(NetSchoolAPIDto):
    lessons: List[Lesson]
    day: date  # alias: date

@dataclass(kw_only=True)
class Diary(NetSchoolAPIDto):
    start: date  # alias: weekStart
    end: date  # alias: weekEnd
    schedule: List[Day]  # alias: weekDays

@dataclass(kw_only=True)
class ShortSchool(NetSchoolAPIDto):
    name: str
    id: int
    address: str  # alias: addressString

@dataclass(kw_only=True)
class School(NetSchoolAPIDto):
    name: str  # alias: fullSchoolName
    about: str
    address: str
    email: str
    site: str  # alias: web
    phone: str  # alias: phones
    director: str
    AHC: str  # alias: principalAHC
    IT: str  # alias: principalIT
    UVR: str  # alias: principalUVR
