import datetime
from datetime import date
from typing import Optional

from pydantic import BaseModel, TypeAdapter

from src.infrastructure.http.schemas import Assignment, AssignmentInfo, Day


class FilterItem(BaseModel):
    """Filter item for reports"""

    title: str
    value: str


class Filter(BaseModel):
    """Filter definition for reports"""

    id: str
    default: str
    items: Optional[list[FilterItem]] = None


class Report(BaseModel):
    """Schema: Report"""

    id: str
    path: str
    title: str
    filters: list[Filter]


class ReportInitData(BaseModel):
    """Schema: ReportInitData"""

    general_title: str
    general: list[Report]
    common_title: str
    common: list[Report]


class AssignmentInfoResponse(BaseModel):
    """API Response: AssignmentInfoResponse"""

    assignment: Assignment
    details: AssignmentInfo


class DiaryResponse(BaseModel):
    """API Response: DiaryResponse"""

    start: datetime.date
    end: datetime.date
    schedule: list[Day]
    class_name: Optional[str]
    term_name: Optional[str]


class WeeksResponse(BaseModel):
    """API Response: WeeksResponse"""

    weeks: list[list[str]]
    start: date
    end: date


class ReportRequest(BaseModel):
    """API Request: ReportRequest"""

    id: str
    filters: Optional[str]
    student_id: Optional[int]


class AttachmentRequest(BaseModel):
    """API Request: AttachmentRequest"""

    attachment_id: int
    student_id: Optional[int]
    assignment_id: Optional[int]


class StudentsResponse(BaseModel):
    id: int
    class_name: str
    class_id: int
    name: str


ListStudentsResponse = TypeAdapter(list[StudentsResponse])
