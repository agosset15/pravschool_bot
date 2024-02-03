import requests
import os
import json
import datetime
from typing import Optional
from db import Student
from ..config import bot, send_greeting, ns
from db.methods.get import get_students_with_duty_notification, get_students_with_greet_notification


async def get_duty(student: Student, student_id: Optional[int] = None) -> str:
    try:
        await ns.login(student.login, student.password, 1)
        ass = await ns.overdue(student_id=student_id)
        if ass is not None:
            arr = []
            for i in ass:
                asss = await ns.assignment_info(i.id, student_id)
                arr.append(f"{i.type} по предмету {asss.subjectGroup.name.split('/')[1]}:\n{asss.name}")
            text = "\n\n".join(arr)
            text = f"Вот ваши долги на данное время:\n\n{text}"
        else:
            text = "На данный момент просроченных заданий нет!"
        await ns.logout()
        await ns.logout()
        await ns.logout()
        return text
    except SchoolNotFoundError or AuthError or NoResponseFromServer:
        await ns.logout()
        return None


async def send_user_ns_duty():
    ids = get_students_with_duty_notification()
    for z in ids:
        await bot.send_message(z.tgid, )


async def send_greet():
    morning = datetime.datetime.now().hour < 14
    req = requests.get(f"https://api.weather.yandex.ru/v2/informers?lat=55.723377&lon=37.600595&lang=ru_RU",
                       headers={"X-Yandex-API-Key": os.getenv('WEATHER_TOKEN')})
    forecast = json.loads(req.json())
    ass_t = {"clear": 'ясно', 'partly-cloudy': 'малооблачно', 'cloudy': 'облачно с прояснениями',
             'overcast': 'пасмурно', 'light-rain': 'небольшой дождь', 'rain': 'дождь', 'heavy-rain': 'сильный дождь',
             'showers': 'ливень', 'wet-snow': 'дождь со снегом', 'light-snow': 'небольшой снег', 'snow': 'снег',
             'snow-showers': 'снегопад', 'hail': 'град', 'thunderstorm': 'гроза',
             'thunderstorm-with-rain': 'дождь с грозой', 'thunderstorm-with-hail': 'гроза с градом.'}
    if morning:
        text = (f"🏙Доброго утра!\n\nСегодня на улице {forecast.fact.temp}({forecast.fact.feels_like})°C, "
                f"{ass_t[forecast.fact.condition]}.\n\n")
    else:
        text = (f"🌃Доброго вечера!\n\nЗавтра на улице {forecast.forecast.parts[1].temp_avg}("
                f"{forecast.forecast.parts[1].feels_like})°C, {ass_t[forecast.forecast.parts[1].condition]}.\n\n")
    for s in get_students_with_greet_notification():
        text = text + await get_duty(s)
        await bot.send_message(student.tgid, text)
