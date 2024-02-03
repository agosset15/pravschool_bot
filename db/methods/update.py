from ..base import Database
from .get import get_student_by_telegram_id
from ..tables import Homework, Schedule, Student


# ```````````````````````````````````````````````STUDENTS`````````````````````````````````````````````````````````


def switch_student_admin(telegram_id: int) -> None:
    student = get_student_by_telegram_id(telegram_id)
    if student:
        student.isAdmin = not student.isAdmin
        Database().session.commit()


def switch_student_ns(telegram_id: int) -> None:
    student = get_student_by_telegram_id(telegram_id)
    if student:
        student.isNs = 1
        Database().session.commit()


def switch_student_parent(telegram_id: int, i: bool = True) -> None:
    student = get_student_by_telegram_id(telegram_id)
    if student:
        student.isParent = int(i)
        Database().session.commit()


def switch_student_teasher_true(telegram_id: int) -> None:
    student = get_student_by_telegram_id(telegram_id)
    if student:
        student.isTeacher = 1
        Database().session.commit()


def switch_student_teasher_false(telegram_id: int) -> None:
    student = get_student_by_telegram_id(telegram_id)
    if student:
        student.isTeacher = 0
        Database().session.commit()


def edit_student_login(telegram_id: int, new_login: str = None) -> None:
    Database().session.query(Student).filter(Student.tgid == telegram_id).update(
        values={Student.login: new_login})
    Database().session.commit()


def edit_student_password(telegram_id: int, new_password: str = None) -> None:
    Database().session.query(Student).filter(Student.tgid == telegram_id).update(
        values={Student.password: new_password})
    Database().session.commit()


def edit_student_clas(telegram_id: int, new_clas: int = None) -> None:
    Database().session.query(Student).filter(Student.tgid == telegram_id).update(
        values={Student.clas: new_clas})
    Database().session.commit()


def switch_student_duty_notification(telegram_id: int) -> None:
    student = get_student_by_telegram_id(telegram_id)
    if student:
        student.duty_notification = not student.duty_notification
        Database().session.commit()


def switch_student_greet_notification(telegram_id: int) -> None:
    student = get_student_by_telegram_id(telegram_id)
    if student:
        student.duty_notification = not student.duty_notification
        Database().session.commit()


def switch_student_greet_notification_time(telegram_id: int, time: int) -> None:
    Database().session.query(Student).filter(Student.tgid == telegram_id).update(
        values={Student.time_to_greet: time})
    Database().session.commit()


def update_student_blocked(user_id: int):
    Database().session.query(Student).filter(Student.tgid == user_id).update(
        values={Student.blocked: 'True'})
    Database().session.commit()


def update_student_nonblocked(user_id: int):
    Database().session.query(Student).filter(Student.tgid == user_id).update(
        values={Student.blocked: 'False'})
    Database().session.commit()


# `````````````````````````````````````````````````````SCHEDULE```````````````````````````````````````````````````


def edit_schedule_rasp(clas: str, day: str, new_rasp: str) -> None:
    Database().session.query(Schedule).filter(Schedule.clas == clas,
                                              Schedule.day == day).update(values={Schedule.rasp: new_rasp})
    Database().session.commit()


# `````````````````````````````````````````````````````HOMEWORKS``````````````````````````````````````````````````

def edit_homework(day: int, lesson: int, clas: int, new_homework: str, image: str|None) -> None:
    Database().session.query(Homework).filter(Homework.day == day, Homework.lesson == lesson,
                                              Homework.clas == clas).update(values={Homework.homework: new_homework,
                                                                                    Homework.image: image})
    Database().session.commit()


def edit_homework_upd_date(day: int, lesson: int, clas: str, new_upd_date: str) -> None:
    Database().session.query(Homework).filter(Homework.day == day, Homework.lesson == lesson,
                                              Homework.clas == clas).update(values={Homework.upd_date: new_upd_date})
    Database().session.commit()
