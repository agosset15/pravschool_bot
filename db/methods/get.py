from sqlalchemy import exc

from ..base import Database
from ..tables import Student, Schedule, Homework


def get_student_by_id(_id: int) -> Student:
    try:
        return Database().session.query(Student).filter(Student.id == _id).one()
    except exc.NoResultFound:
        return None


def get_student_by_telegram_id(telegram_id: int) -> Student:
    try:
        return Database().session.query(Student).filter(Student.id == telegram_id).one()
    except exc.NoResultFound:
        return None


def get_all_students() -> list[Student]:
    try:
        return Database().session.query(Student).filter(Student.blocked == 'False').all()
    except exc.NoResultFound:
        return None


def get_students_with_admin() -> list[Student]:
    try:
        return Database().session.query(Student).filter(Student.isAdmin == 1).all()
    except exc.NoResultFound:
        return None


def get_students_with_teacher() -> list[Student]:
    try:
        return Database().session.query(Student).filter(Student.isTeacher == 1).all()
    except exc.NoResultFound:
        return None


def get_all_classes() -> list:
    try:
        clas_from_students = Database().session.query(Student.clas).all()
        return clas_from_students
    except exc.NoResultFound:
        return None


def get_students_with_duty_notification() -> list[Student]:
    try:
        return Database().session.query(Student).filter(Student.duty_notification == 1, Student.blocked == 'False').all()
    except exc.NoResultFound:
        return None


def get_schedule(clas: int, day: int) -> Schedule.rasp:
    try:
        return Database().session.query(Schedule.rasp).filter(Schedule.clas == clas, Schedule.day == day,
                                                              Schedule.isTeacher == 0, Schedule.isKab == 0).one()[0]
    except exc.NoResultFound:
        return None


def get_teacher_schedule(clas: int, day: int) -> Schedule.rasp:
    try:
        return Database().session.query(Schedule.rasp).filter(Schedule.clas == clas, Schedule.day == day,
                                                              Schedule.isTeacher == 1, Schedule.isKab == 0).one()[0]
    except exc.NoResultFound:
        return None


def get_kab_schedule(clas: int, day: int) -> Schedule.rasp:
    try:
        return Database().session.query(Schedule.rasp).filter(Schedule.clas == clas, Schedule.day == day,
                                                              Schedule.isTeacher == 1, Schedule.isKab == 1).one()[0]
    except exc.NoResultFound:
        return None


def get_homework(lesson: int, clas: int, day: int) -> Homework:
    try:
        return Database().session.query(Homework).filter(Homework.lesson == lesson, Homework.clas == clas,
                                                         Homework.day == day).one()
    except exc.NoResultFound:
        return None


def get_count() -> int:
    return Database().session.query(Student).count()
