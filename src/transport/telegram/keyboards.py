from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InlineQueryResultUnion,
    InputTextMessageContent,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from fluentogram import TranslatorRunner

from src.core.config import AppConfig
from src.core.constants import GOTO_PREFIX
from src.core.dto import ScheduleDto
from src.core.enums import InlineQueryText, WeekDay
from src.transport.telegram.states import DashboardUser, NSCredentials, Register


def get_user_keyboard(
    telegram_id: int,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text="btn-goto.user-profile",
            callback_data=f"{GOTO_PREFIX}{DashboardUser.MAIN.state}:{telegram_id}",
        ),
    )
    return builder.as_markup()

def get_time_keyboard(display: bool = True, week: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    callback_data = "get_time"
    if week:
        callback_data += "-week"
    if display:
        callback_data += "-show"
    else:
        callback_data += "-hide"
    builder.row(
        InlineKeyboardButton(
            text="btn-time.display" if display else "btn-time.hide",
            callback_data=callback_data,
        ),
    )
    return builder.as_markup()

def get_register_grade_keyboard(
    telegram_id: int,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text="btn-goto.register-grade",
            callback_data=f"{GOTO_PREFIX}{Register.GRADE.state}:{telegram_id}",
        ),
    )
    return builder.as_markup()

def get_ns_add_credentials_keyboard(
    telegram_id: int,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text="btn-goto.ns-credentials",
            callback_data=f"{GOTO_PREFIX}{NSCredentials.LOGIN.state}:{telegram_id}",
        ),
    )
    return builder.as_markup()


def inline_grade_results(
        schedule: ScheduleDto,
        i18n: TranslatorRunner,
        config: AppConfig,
        reply_markup: InlineKeyboardMarkup
) -> list[InlineQueryResultUnion]:
    results: list[InlineQueryResultUnion] = []
    week = []
    thumbnail_names = WeekDay.names()
    for i, day in enumerate(schedule.days):
        text = f"<b>{day.name}</b>:\n{day.text}"
        results.append(InlineQueryResultArticle(
            id=f"{day.name.name}_{schedule.grade}",
            title=day.name.get_text(i18n),
            input_message_content=InputTextMessageContent(
                message_text=f"{schedule.grade}: {text}", parse_mode="HTML"
            ),
            reply_markup=reply_markup,
            thumbnail_url=config.static_path(thumbnail_names[i] + "png"),
            thumbnail_width=512, thumbnail_height=512
        ))
        week.append(text)
    results.append(InlineQueryResultArticle(
        id=f"week_{schedule.grade}",
        title=i18n.get("week"),
        input_message_content=InputTextMessageContent(
            message_text=f"{schedule.grade}: " + "\n\n".join(week), parse_mode="HTML"),
        reply_markup=reply_markup,
        thumbnail_url=config.static_path("week.png"),
        thumbnail_height=512, thumbnail_width=512
    ))
    return results


def inline_schedule_results(
        schedules: list[ScheduleDto], prefix: InlineQueryText
) -> list[InlineQueryResultUnion]:
    buttons: list[InlineQueryResultUnion] = []
    for schedule in schedules:
        buttons.append(InlineQueryResultArticle(id=f"{prefix}_{schedule.id}", title=schedule.grade,
                                                input_message_content=InputTextMessageContent(
                                                    message_text=f"{prefix}_{schedule.id}")))
    return buttons


def inline_kb(**data_text: str) -> InlineKeyboardMarkup:
    """Create inline keyboard with callback buttons."""
    builder = InlineKeyboardBuilder()
    for callback_data, text in data_text.items():
        builder.button(text=text, callback_data=callback_data)
    builder.adjust(1)
    return builder.as_markup()


def reply_kb(*texts: str, placeholder: str | None = None, adjust: int = 1) -> ReplyKeyboardMarkup:
    """Create reply keyboard with text buttons."""
    builder = ReplyKeyboardBuilder()
    for text in texts:
        builder.button(text=text)
    builder.adjust(adjust)
    return builder.as_markup(resize_keyboard=True, input_field_placeholder=placeholder)


def remove_kb() -> ReplyKeyboardRemove:
    """Remove keyboard."""
    return ReplyKeyboardRemove()


def url_kb(**url_text: str) -> InlineKeyboardMarkup:
    """Create keyboard with URL buttons."""
    builder = InlineKeyboardBuilder()
    for url, text in url_text.items():
        builder.button(text=text, url=url)
    builder.adjust(1)
    return builder.as_markup()


def switch_inline_kb(text: str, param: str) -> InlineKeyboardMarkup:
    """Create keyboard with switch inline query button."""
    builder = InlineKeyboardBuilder()
    builder.button(text=text, switch_inline_query_current_chat=param)
    builder.adjust(1)
    return builder.as_markup()
