import re
from datetime import timezone
from pathlib import Path
from re import Pattern
from typing import Final

BASE_DIR: Final[Path] = Path(__file__).resolve().parents[2]
ASSETS_DIR: Final[Path] = BASE_DIR / "assets"
LOG_DIR: Final[Path] = BASE_DIR / "logs"

DOMAIN_REGEX: Pattern[str] = re.compile(r"^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$")
TAG_REGEX: Pattern[str] = re.compile(r"^[A-Z0-9_]{1,16}$")
URL_PATTERN: Pattern[str] = re.compile(r"^https?://.*$")
USERNAME_PATTERN: Pattern[str] = re.compile(r"^@[a-zA-Z0-9_]{5,32}$")

REPOSITORY: Final[str] = "https://github.com/agosset15/pravschool_bot"
T_ME: Final[str] = "https://t.me/"
API_ENDPOINT: Final[str] = "/api"
BOT_WEBHOOK_ENDPOINT: Final[str] = "/webhook/pravschool_bot"

DEEPLINK_PREFIX: Final[str] = "?start="
GOTO_PREFIX: Final[str] = "go_"
ENCRYPTED_PREFIX: Final[str] = "enc_"

MIDDLEWARE_DATA_KEY: Final[str] = "middleware_data"
CONTAINER_KEY: Final[str] = "dishka_container"
CONFIG_KEY: Final[str] = "config"
USER_KEY: Final[str] = "user"
GRADES_KEY: Final[str] = "grades"
TARGET_TELEGRAM_ID: Final[str] = "target_telegram_id"

LESSON_TIMES: Final[list[str]] = [
    "08:40 - 09:25",
    "09:35 - 10:20",
    "10:30 - 11:15",
    "11:25 - 12:10",
    "12:25 - 13:10",
    "13:25 - 14:10",
    "14:25 - 15:10",
    "15:20 - 16:05",
    "16:15 - 17:00",
    "17:00 - (?)"
]

TIMEZONE: Final[timezone] = timezone.utc
DATETIME_FORMAT: Final[str] = "%d.%m.%Y %H:%M:%S"

TIME_1M: Final[int] = 60
TIME_1H: Final[int] = TIME_1M * 60
TIME_1D: Final[int] = TIME_1H * 24

TTL_5M: Final[int] = TIME_1M * 5
TTL_10M: Final[int] = TIME_1M * 10
TTL_30M: Final[int] = TIME_1M * 30
TTL_1H: Final[int] = TIME_1H
TTL_6H: Final[int] = TIME_1H * 6
TTL_12H: Final[int] = TIME_1H * 12
TTL_1D: Final[int] = TIME_1D
TTL_7D: Final[int] = TIME_1D * 7

RECENT_REGISTERED_MAX_COUNT: Final[int] = 25
RECENT_ACTIVITY_MAX_COUNT: Final[int] = 25

BATCH_SIZE_10: Final[int] = 10
BATCH_SIZE_20: Final[int] = 20
BATCH_DELAY: Final[int] = 1

COMMA: Final[str] = ","
