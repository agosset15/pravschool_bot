from sqlalchemy import Column, Integer, String, Boolean

from .base import Database


class Student(Database.BASE):
    __tablename__ = 'STUDENTS'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    username = Column(String)
    isAdmin = Column(Boolean, default=False)
    isNs = Column(Boolean, default=False)
    isTeacher = Column(Boolean, default=False)
    login = Column(String)
    password = Column(String)
    clas = Column(Integer)
    duty_notification = Column(Boolean, default=False)
    blocked = Column(String, default='False')
    ref = Column(String)


class Schedule(Database.BASE):
    __tablename__ = 'SCHEDULE'

    id = Column(Integer, primary_key=True)
    isTeacher = Column(Boolean)
    isKab = Column(Boolean)
    clas = Column(Integer)
    day = Column(Integer)
    rasp = Column(String)


class Homework(Database.BASE):
    __tablename__ = 'HOMEWORKS'

    id = Column(Integer, primary_key=True)
    day = Column(Integer)
    lesson = Column(Integer)
    clas = Column(Integer)
    homework = Column(String)
    upd_date = Column(String)


def register_models():
    Database.BASE.metadata.create_all(Database().engine)
