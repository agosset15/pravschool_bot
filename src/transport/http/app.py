from aiogram import Dispatcher
from fastapi import APIRouter, FastAPI
from loguru import logger
from starlette.middleware.cors import CORSMiddleware

from src.core.config import AppConfig
from src.core.constants import API_ENDPOINT, BOT_WEBHOOK_ENDPOINT
from src.lifespan import lifespan

from .endpoints import TelegramWebhookEndpoint, api


def get_app(config: AppConfig, dispatcher: Dispatcher) -> FastAPI:
    app: FastAPI = FastAPI(
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        include_in_schema=False,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    api_router = APIRouter(prefix=API_ENDPOINT)
    for router in api.routers:
        api_router.include_router(router)

    telegram_webhook_endpoint = TelegramWebhookEndpoint(
        dispatcher=dispatcher,
        secret_token=config.bot.secret_token.get_secret_value(),
    )

    telegram_webhook_endpoint.register(app=app, path=BOT_WEBHOOK_ENDPOINT)

    app.state.telegram_webhook_endpoint = telegram_webhook_endpoint
    app.state.dispatcher = dispatcher

    logger.info("FastAPI application initialized'")
    return app
