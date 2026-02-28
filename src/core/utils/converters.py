import re
from calendar import monthrange
from datetime import datetime, timedelta
from typing import Optional

from src.core.utils.time import datetime_now


def to_snake_case(name: str) -> str:
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def event_to_key(class_name: str) -> str:
    snake = re.sub(r"(?<!^)(?=[A-Z])", "_", class_name).lower()
    formatted_key = snake.replace("_", "-")
    return f"event-{formatted_key}"


def percent(part: int, whole: int) -> str:
    if whole == 0:
        return "N/A"

    percent = (part / whole) * 100
    return f"{percent:.2f}"


def country_code_to_flag(code: str) -> str:
    if not code.isalpha() or len(code) != 2:
        return "🏴‍☠️"

    return "".join(chr(ord("🇦") + ord(c.upper()) - ord("A")) for c in code)


def days_to_datetime(value: int, year: int = 2099) -> datetime:
    dt = datetime_now()

    if value == 0:  # UNLIMITED for panel
        try:
            return dt.replace(year=year)
        except ValueError:
            last_day = monthrange(year, dt.month)[1]
            return dt.replace(year=year, day=min(dt.day, last_day))

    return dt + timedelta(days=value)

def dashes_to_dots_date(date: str) -> str:
    return datetime.strptime(date, "%Y-%m-%d").strftime("%d.%m.%Y")  # noqa: DTZ007

def parse_referral_code(text: str) -> Optional[str]:
    parts = text.split()

    if len(parts) <= 1:
        return None

    code = parts[1]

    return code
