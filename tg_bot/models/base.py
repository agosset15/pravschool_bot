# Import all the models, so that Base has them before being
# imported by Alembic

from .user import User
from .schedule import Schedule, Homework, Day, Lesson

__all__ = (
    "User",
    "Schedule",
    "Homework",
    "Day",
    "Lesson",
)
