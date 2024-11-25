from datetime import datetime, timedelta
from typing import Optional, List

from aiogram import html, Bot
from aiogram.utils.link import create_telegram_link

from netschoolapi import NetSchoolAPI
from netschoolapi.errors import AuthError, NoResponseFromServer
from netschoolapi.schemas import Day, Assignment
from tg_bot.models import User
from tg_bot.config import NS_URL, cache
from tg_bot.misc import ns_sessions


class NSError(Exception):
    """Error caused on logging in NS account"""


class DayNotFound(Exception):
    """Probably this day is a weekend day or a holiday"""


def parse_day(bot_username: str, day: Day, student_id: int):
    message_text = []
    for lesson in day.lessons:
        if lesson.assignments:
            for assignment in lesson.assignments:
                link = create_telegram_link(bot_username + '/journal',
                                            startapp=f"{day.day.strftime('%Ya%ma%d')}a{lesson.lesson_id}a"
                                                     f"{assignment.id}a{student_id}")
                text = f"{html.bold(assignment.type)}({lesson.subject}) {html.link('·?·', link)}\n{assignment.content}"
                if assignment.mark is None:
                    if assignment.is_duty is True:
                        text = "⚠️ДОЛГ!\n" + text
                else:
                    text = text + f" -- {html.bold(assignment.mark)}"
                message_text.append(text)
        else:
            message_text.append(f"{html.bold(lesson.subject)}\nЗаданий нет.")
    return "\n\n".join(message_text)


async def parse_duty(bot_username: str, assignments: List[Assignment], ns: NetSchoolAPI, student_id: int = None):
    message_text = []
    for assignment in assignments:
        info = await ns.assignment_info(assignment.id, student_id=student_id)
        link = create_telegram_link(bot_username, 'journal', startapp=f"{info.id}a{ns.current_student}")
        message_text.append(f"{assignment.type} по предмету {info.subject.name} {html.link('·?·', link)}:\n{info.name}")
    return f"Вот ваши долги на данное время:\n\n{'\n\n'.join(message_text)}"


async def get_ns_day(start: datetime, day: int, bot: Bot, ns: NetSchoolAPI,
                     student_id: int = None) -> str:
    bot_username = (await bot.get_me()).username
    day_date = datetime.date(start + timedelta(days=day))
    try:
        # TODO: сделать выбор другой школы в настройках ЭЖ
        diary = await ns.diary(start=start, student_id=student_id)
    except NoResponseFromServer:
        raise NoResponseFromServer("Нет ответа от сервера. Повторите попытку.")

    day = next((item for item in diary.schedule if item.day == day_date), None)
    if day is None:
        raise DayNotFound("День является выходным, или уроки в него еще не добавлены.")

    children = []
    for student in ns.students:
        children.append(student['nickName'])
    return parse_day(bot_username, day, ns.current_student)


async def get_duty(bot: Bot, ns: NetSchoolAPI, student_id: Optional[int] = None) -> str:
    bot_username = (await bot.get_me()).username
    try:
        # TODO: сделать выбор другой школы в настройках ЭЖ
        assignments = await ns.overdue(student_id=student_id)
    except NoResponseFromServer:
        raise NoResponseFromServer("Нет ответа от сервера. Повторите попытку.")
    if assignments is not None:
        return await parse_duty(bot_username, assignments, ns, student_id)
    return "На данный момент просроченных заданий нет!"


async def get_ns_object(user: User) -> NetSchoolAPI:
    if user.id not in ns_sessions.keys() and user.is_ns:
        ns = NetSchoolAPI(NS_URL)
        await ns.login(user.login, user.password, 1, requests_timeout=120)
        ns_sessions.update({user.id: ns})
    return ns_sessions.get(user.id, NetSchoolAPI(NS_URL))


async def update_ns_object(user: User, ns: NetSchoolAPI):
    return ns_sessions.update({user.id: ns})


async def encode_ns_password(ns: NetSchoolAPI, login: str, password: str) -> str:
    try:
        encoded_password = await ns.login(login, password, 1, password_encode=True, requests_timeout=120)
        return encoded_password
    except AuthError:
        await ns.logout()
        raise NSError("Неверные данные. Попробуйте еще раз.\nПришлите ваш логин для входа в электронный журнал")
