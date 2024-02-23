from ..base import Database
from ..tables import Schedule, Student
from .get import get_student_by_telegram_id, get_homework, get_schedule


def delete_student(telegram_id: int):
    try:
        sts = Database().session.query(Student).filter(Student.tgid == telegram_id).all()
        for st in sts:
            Database().session.delete(st)
    except exc.NoResultFound:
        return None


def delete_schedules():
    session = Database().session
    session.query(Schedule).delete()


def delete_schedule_day(clas: int, day: int):
    session = Database().session
    schedule = get_schedule(clas, day)

    if schedule:
        session.drop(schedule)
        session.commit()


def delete_homework(lesson: str, clas: str):
    session = Database().session
    homework = get_homework(lesson, clas)

    if homework:
        session.delete(homework)
        session.commit()
