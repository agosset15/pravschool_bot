import asyncio
import base64
import string
import traceback
import uuid
from dataclasses import asdict
from typing import Any, Callable, Optional, Union, cast

from adaptix import Retort
from adaptix.conversion import ConversionRetort
from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError
from aiogram.types import (
    BufferedInputFile,
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    ReplyKeyboardMarkup,
)
from aiogram.utils.formatting import Text
from aiogram.utils.keyboard import InlineKeyboardBuilder
from fluentogram import TranslatorHub
from loguru import logger
from redis.asyncio import Redis

from src.core.config import AppConfig
from src.core.dto import MediaDescriptorDto, MessagePayloadDto, TempUserDto, UserDto
from src.core.enums import (
    Locale,
    MediaType,
    SystemNotificationType,
    UserRole,
)
from src.core.types import AnyKeyboard
from src.transport.telegram.states import Notification

from .base import BaseService
from .user import UserService


class NotificationService(BaseService):
    user_service: UserService

    def __init__(
        self,
        config: AppConfig,
        bot: Bot,
        redis: Redis,
        retort: Retort,
        conversion_retort: ConversionRetort,
        #
        translator_hub: TranslatorHub,
        user_service: UserService,
    ) -> None:
        super().__init__(config, bot, redis, retort, conversion_retort)
        self.user_service = user_service
        self.translator_hub = translator_hub

    async def notify_user(
        self,
        user: Optional[Union[UserDto, TempUserDto]],
        payload: MessagePayloadDto,
    ) -> Optional[Message]:
        if not user:
            logger.warning("Skipping user notification: user object is empty")
            return None

        logger.debug(
            f"Attempting to send user notification '{payload.i18n_key}' to '{user.telegram_id}'"
        )

        return await self._send_message(user, payload)

    async def system_notify(
        self,
        payload: MessagePayloadDto,
        ntf_type: SystemNotificationType,
    ) -> list[bool]:
        payload.delete_after = None
        if self.config.bot.topic_logs_enabled:
            devs = [self._get_topic_logs_chat_user()]
            thread_id = ntf_type.get_logs_topic(self.config.bot.list_topic_logs_threads)
        else:
            devs = await self.user_service.get_by_role(role=UserRole.DEV)
            thread_id = None

        if not devs:
            devs = [self._get_temp_owner()]

        logger.debug(
            f"Attempting to send system notification '{payload.i18n_key}' to '{len(devs)}' devs"
        )

        async def send_to_dev(dev: UserDto) -> bool:
            return bool(await self._send_message(user=dev, payload=payload, thread_id=thread_id))

        tasks = [send_to_dev(dev) for dev in devs]
        results = await asyncio.gather(*tasks)

        return cast(list[bool], cast(object, results))

    async def notify_super_dev(self, payload: MessagePayloadDto) -> bool:
        dev = await self.user_service.get(telegram_id=self.config.bot.owner_id)

        if not dev:
            dev = self._get_temp_owner()

        logger.debug(
            f"Attempting to send super dev notification '{payload.i18n_key}' to '{dev.telegram_id}'"
        )

        return bool(await self._send_message(user=dev, payload=payload))

    async def error_notify(
        self,
        exception: BaseException,
        payload: MessagePayloadDto,
        error_id: Optional[Union[str, int]] = str(uuid.uuid4()),
    ) -> None:
        payload.delete_after = None
        error_type = type(exception).__name__
        error_message = Text(str(exception)[:512])

        traceback_str = "".join(
            traceback.format_exception(
                type(exception),
                exception,
                exception.__traceback__,
            )
        )
        payload.i18n_kwargs.update(
            {
                "error": f"{error_type}: {error_message.as_html()}"
            }
        )
        payload.media = MediaDescriptorDto(
            kind="bytes",
            value=base64.b64encode(traceback_str.encode("utf-8")).decode(),
            filename=f"error_{error_id}.txt",
        )
        payload.media_type = MediaType.DOCUMENT
        await self.notify_super_dev(payload=payload)

    #

    async def _send_message(
        self,
        user: Union[UserDto, TempUserDto],
        payload: MessagePayloadDto,
        thread_id: Optional[int] = None,
    ) -> Optional[Message]:
        render_kwargs = payload.i18n_kwargs.copy()

        if isinstance(user, UserDto) and payload.i18n_key == "ntf-broadcast.message":
            user_data = asdict(user)
            render_kwargs = {**user_data, **payload.i18n_kwargs}

        reply_markup = self._prepare_reply_markup(
            payload.reply_markup,
            payload.disable_default_markup,
            payload.delete_after,
            self.config.default_locale,
            user.telegram_id,
        )

        text = self._get_translated_text(
            locale=self.config.default_locale,
            i18n_key=payload.i18n_key,
            i18n_kwargs=render_kwargs,
        )

        kwargs: dict[str, Any] = {
            "disable_notification": payload.disable_notification,
            "message_effect_id": payload.message_effect,
            "reply_markup": reply_markup,
            "message_thread_id": thread_id,
        }

        try:
            if payload.is_text:
                message = await self.bot.send_message(
                    chat_id=user.telegram_id,
                    text=text,
                    disable_web_page_preview=True,
                    **kwargs,
                )
            elif payload.media:
                method = self._get_media_method(payload)
                media = self._build_media(payload.media)

                if not method:
                    logger.warning(f"Unknown media type for payload '{payload}'")
                    return None

                message = await method(user.telegram_id, media, caption=text, **kwargs)
            else:
                logger.error(f"Payload must contain text or media for user '{user.telegram_id}'")
                return None

            if message and payload.delete_after:
                asyncio.create_task(
                    self._schedule_message_deletion(
                        chat_id=user.telegram_id,
                        message_id=message.message_id,
                        delay=payload.delete_after,
                    )
                )

            return message

        except TelegramForbiddenError:
            logger.warning(f"Bot was blocked by user '{user.telegram_id}'")
            return None
        except Exception as e:
            logger.exception(f"Failed to send notification to '{user.telegram_id}': {e}")
            raise

    def _get_media_method(self, payload: MessagePayloadDto) -> Optional[Callable[..., Any]]:
        if payload.is_photo:
            return self.bot.send_photo

        if payload.is_video:
            return self.bot.send_video

        if payload.is_document:
            return self.bot.send_document

        return None

    def _prepare_reply_markup(
        self,
        reply_markup: Optional[AnyKeyboard],
        add_close_button: bool,
        auto_delete_after: Optional[int],
        locale: Locale,
        chat_id: int,
    ) -> Optional[AnyKeyboard]:
        if reply_markup is None:
            if add_close_button and auto_delete_after is None:
                close_button = self._get_close_notification_button(locale=locale)
                return self._get_default_keyboard(close_button)
            return None

        if not add_close_button or auto_delete_after is not None:
            return self._translate_keyboard_texts(reply_markup, locale)

        close_button = self._get_close_notification_button(locale=locale)

        if isinstance(reply_markup, InlineKeyboardMarkup):
            translated_markup = self._translate_keyboard_texts(reply_markup, locale)
            translated_markup = cast(InlineKeyboardMarkup, translated_markup)
            builder = InlineKeyboardBuilder.from_markup(translated_markup)
            builder.row(close_button)
            return builder.as_markup()

        if isinstance(reply_markup, ReplyKeyboardMarkup):
            return self._translate_keyboard_texts(reply_markup, locale)

        logger.warning(
            f"Unsupported reply_markup type '{type(reply_markup).__name__}' "
            f"for chat '{chat_id}'. Close button will not be added"
        )
        return reply_markup

    def _get_close_notification_button(self, locale: Locale) -> InlineKeyboardButton:
        text = self._get_translated_text(locale, "btn-common.notification-close")
        return InlineKeyboardButton(text=text, callback_data=Notification.CLOSE.state)

    @staticmethod
    def _get_default_keyboard(button: InlineKeyboardButton) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder([[button]])
        return builder.as_markup()

    async def _schedule_message_deletion(self, chat_id: int, message_id: int, delay: int) -> None:
        logger.debug(
            f"Scheduling message '{message_id}' for auto-deletion in '{delay}' (chat '{chat_id}')"
        )
        try:
            await asyncio.sleep(delay)
            await self.bot.delete_message(chat_id=chat_id, message_id=message_id)
            logger.debug(
                f"Message '{message_id}' in chat '{chat_id}' deleted after '{delay}' seconds"
            )
        except Exception as exception:
            logger.error(
                f"Failed to delete message '{message_id}' in chat '{chat_id}': {exception}"
            )

    def _get_translated_text(
        self,
        locale: Locale,
        i18n_key: str,
        i18n_kwargs: dict[str, Any] = {},
    ) -> str:
        if not i18n_key:
            return ""

        i18n = self.translator_hub.get_translator_by_locale(locale)
        translated_text = i18n.get(i18n_key, **i18n_kwargs)

        if i18n_key == "ntf-broadcast.message":
            if "$" in translated_text and i18n_kwargs:
                template = string.Template(translated_text)
                return template.safe_substitute(i18n_kwargs)

        return translated_text

    def _translate_keyboard_texts(self, keyboard: AnyKeyboard, locale: Locale) -> AnyKeyboard:  # noqa: C901
        if isinstance(keyboard, InlineKeyboardMarkup):
            new_inline_keyboard = []

            for row_inline in keyboard.inline_keyboard:
                new_row_inline = []
                for button_inline in row_inline:
                    if button_inline.text:
                        try:
                            button_inline.text = self._get_translated_text(
                                locale, button_inline.text
                            )
                        except Exception:
                            button_inline.text = button_inline.text
                    new_row_inline.append(button_inline)
                new_inline_keyboard.append(new_row_inline)

            return InlineKeyboardMarkup(inline_keyboard=new_inline_keyboard)

        elif isinstance(keyboard, ReplyKeyboardMarkup):
            new_keyboard = []

            for row in keyboard.keyboard:
                new_row = []
                for button in row:
                    if button.text:
                        try:
                            button.text = self._get_translated_text(locale, button.text)
                        except Exception:
                            button.text = button.text
                    new_row.append(button)
                new_keyboard.append(new_row)

            return ReplyKeyboardMarkup(
                keyboard=new_keyboard, **keyboard.model_dump(exclude={"keyboard"})
            )

        return keyboard

    def _get_temp_owner(self) -> UserDto:
        temp_dev = UserDto(
            telegram_id=self.config.bot.owner_id,
            name="TempDev",
            role=UserRole.DEV,
        )

        logger.warning("Fallback to temporary dev user from environment for notifications")
        return temp_dev

    def _get_topic_logs_chat_user(self) -> UserDto:
        return UserDto(
            telegram_id=self.config.bot.topic_logs_chat_id,
            name="TopicLogsChat",
            role=UserRole.DEV,
        )

    @staticmethod
    def _build_media(media: MediaDescriptorDto) -> Union[str, BufferedInputFile, FSInputFile]:
        if media.kind == "file_id":
            return media.value

        if media.kind == "fs":
            return FSInputFile(
                path=media.value,
                filename=media.filename,
            )

        if media.kind == "bytes":
            return BufferedInputFile(
                file=base64.b64decode(media.value),
                filename=media.filename or "file.bin",
            )

        raise ValueError(f"Unsupported media kind '{media.kind}'")