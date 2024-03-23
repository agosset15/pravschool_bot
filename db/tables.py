from sqlalchemy import Column, Integer, String, Boolean, BigInteger

from .base import Database


class Student(Database.BASE):
    __tablename__ = 'STUDENTS'
    id = Column(Integer, primary_key=True, autoincrement=True)
    tgid = Column(BigInteger, primary_key=True)
    name = Column(String(255))
    username = Column(String(255))
    isAdmin = Column(Boolean, default=False)
    isNs = Column(Boolean, default=False)
    isTeacher = Column(Boolean, default=False)
    isParent = Column(Boolean, default=False)
    defaultChild = Column(Integer)
    login = Column(String(255))
    password = Column(String(255))
    clas = Column(Integer)
    duty_notification = Column(Boolean, default=False)
    greet_notification = Column(Boolean, default=False)
    time_to_greet = Column(Integer, default=2000)
    blocked = Column(String(255), default='False')
    ref = Column(String(255))


class Schedule(Database.BASE):
    __tablename__ = 'SCHEDULE'

    id = Column(Integer, primary_key=True, autoincrement=True)
    isTeacher = Column(Boolean)
    isKab = Column(Boolean)
    clas = Column(Integer)
    day = Column(Integer)
    rasp = Column(String(300))


class Homework(Database.BASE):
    __tablename__ = 'HOMEWORKS'

    id = Column(Integer, primary_key=True, autoincrement=True)
    day = Column(Integer)
    lesson = Column(Integer)
    clas = Column(Integer)
    homework = Column(String(255))
    image = Column(String(255))
    upd_date = Column(String(255))


def register_models():
    Database.BASE.metadata.create_all(Database().engine)
