import requests
import os
import json
from ..config import send_duty, send_greeting
from db.methods.get import get_students_with_duty_notification, get_students_with_greet_notification


async def send_user_ns_duty():
    ids = get_students_with_duty_notification()
    for z in ids:
        await send_duty(z)


async def send_greet(morning: bool = False):
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
        await send_greeting(s, text, morning)
