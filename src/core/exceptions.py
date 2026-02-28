class NetSchoolError(Exception):
    """Base class for all NetSchool errors."""

class NetSchoolAPIError(NetSchoolError):
    pass

class AuthError(NetSchoolAPIError):
    """Error caused on logging in NS account."""

class SchoolNotFoundError(NetSchoolAPIError):
    pass

class NoResponseFromServerError(NetSchoolAPIError):
    """Timeout exceeded while waiting for response from server."""

class DayNotFoundError(NetSchoolError):
    """Probably this day is a weekend day or a holiday."""

class LessonNotFoundError(NetSchoolError):
    """Lesson not found."""

class AssignmentNotFoundError(NetSchoolError):
    """Assignment not found."""

class YearNotFoundError(NetSchoolError):
    """Year schedule image not found."""


class MenuRenderError(Exception): ...