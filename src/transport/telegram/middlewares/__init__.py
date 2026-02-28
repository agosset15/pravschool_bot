from aiogram import Router

from .base import EventTypedMiddleware
from .error import ErrorMiddleware
from .user import UserMiddleware


def setup_middlewares(router: Router) -> None:
    """Setup all middlewares for the Telegram router."""
    outer_middlewares: list[EventTypedMiddleware] = [
        UserMiddleware(),
        ErrorMiddleware(),
    ]
    for middleware in outer_middlewares:
        middleware.setup_outer(router=router)


__all__ = ["setup_middlewares"]
