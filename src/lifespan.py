import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from aiogram import Bot, Dispatcher
from aiogram.types import WebhookInfo
from dishka import AsyncContainer, Scope
from fastapi import FastAPI
from loguru import logger

from src.core.dto import MessagePayloadDto
from src.core.enums import SystemNotificationType
from src.services.notification import NotificationService
from src.services.webhook import WebhookService
from src.transport.http.endpoints import TelegramWebhookEndpoint


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    dispatcher: Dispatcher = app.state.dispatcher
    telegram_webhook_endpoint: TelegramWebhookEndpoint = app.state.telegram_webhook_endpoint
    container: AsyncContainer = app.state.dishka_container

    async with container(scope=Scope.REQUEST) as startup_container:
        webhook_service = await startup_container.get(WebhookService)
        notification_service: NotificationService = await startup_container.get(NotificationService)

        allowed_updates = dispatcher.resolve_used_update_types()
        webhook_info: WebhookInfo = await webhook_service.setup(allowed_updates)

        if webhook_service.has_error(webhook_info):
            logger.critical(
                f"Webhook has a last error message: '{webhook_info.last_error_message}'"
            )
            await notification_service.system_notify(
                ntf_type=SystemNotificationType.ERROR,
                payload=MessagePayloadDto(
                    i18n_key="ntf-event-error-webhook",
                    i18n_kwargs={"error": webhook_info.last_error_message},
                    delete_after=None
                ),
            )

    await telegram_webhook_endpoint.startup()

    bot = await container.get(Bot)
    bot_info = await bot.get_me()
    states: dict[Optional[bool], str] = {True: "Enabled", False: "Disabled", None: "Unknown"}

    logger.opt(colors=True).info(
        rf"""
        <cyan>8888888b.                                             888                        888      888888b.            888    </>
        <cyan>888   Y88b                                            888                        888      888  "88b           888    </>
        <cyan>888    888                                            888                        888      888  .88P           888    </>
        <cyan>888   d88P 888d888 8888b.  888  888 .d8888b   .d8888b 88888b.   .d88b.   .d88b.  888      8888888K.   .d88b.  888888 </>
        <cyan>8888888P"  888P"      "88b 888  888 88K      d88P"    888 "88b d88""88b d88""88b 888      888  "Y88b d88""88b 888    </>
        <cyan>888        888    .d888888 Y88  88P "Y8888b. 888      888  888 888  888 888  888 888      888    888 888  888 888    </>
        <cyan>888        888    888  888  Y8bd8P       X88 Y88b.    888  888 Y88..88P Y88..88P 888      888   d88P Y88..88P Y88b.  </>
        <cyan>888        888    "Y888888   Y88P    88888P'  "Y8888P 888  888  "Y88P"   "Y88P"  888      8888888P"   "Y88P"   "Y888 </>

        <cyan>------------------------</>
        Groups Mode  - {states[bot_info.can_join_groups]}
        Privacy Mode - {states[not bot_info.can_read_all_group_messages]}
        Inline Mode  - {states[bot_info.supports_inline_queries]}
        """  # noqa: E501
    )

    await notification_service.system_notify(
        ntf_type=SystemNotificationType.BOT_LIFECYCLE,
        payload=MessagePayloadDto(
            i18n_key="ntf-event-bot-startup",
            delete_after=None
        ),
    )

    yield

    await notification_service.system_notify(
        ntf_type=SystemNotificationType.BOT_LIFECYCLE,
        payload=MessagePayloadDto(i18n_key="ntf-event-bot-shutdown", delete_after=None),
    )

    await asyncio.sleep(2)

    await telegram_webhook_endpoint.shutdown()
    await webhook_service.delete()
    await container.close()
