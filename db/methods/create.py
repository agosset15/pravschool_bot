import sqlalchemy.exc

from ..base import Database
from ..tables import Student, Homework, Schedule


def create_student(telegram_id: int, name: str, uname: str, clas: int, ref: str) -> None:
    session = Database().session
    try:
        session.query(Student.id).filter(Student.id == telegram_id).one()
    except sqlalchemy.exc.NoResultFound:
        session.add(Student(id=telegram_id, name=name, username=uname, clas=clas, ref=ref))
        session.commit()


def create_schedule(clas: int, day: int, rasp: str, teacher: int, kab: int) -> None:
    session = Database().session
    try:
        session.query(Schedule).filter(Schedule.clas == clas, Schedule.day == day,
                                       Schedule.isTeacher == teacher, Schedule.isKab == kab).one()
    except sqlalchemy.exc.NoResultFound:
        session.add(Schedule(clas=clas, day=day, rasp=rasp, isTeacher=teacher, isKab=kab))
        session.commit()


def create_homework(day: int, lesson: int, clas: int, homework: str, upd_date: str, image: str = None) -> None:
    session = Database().session
    try:
        session.query(Homework).filter(Homework.day == day, Homework.lesson == lesson, Homework.clas == clas).one()
    except sqlalchemy.exc.NoResultFound:
        session.add(Homework(day=day, lesson=lesson, clas=clas, homework=homework, upd_date=upd_date, image=image))
        session.commit()
