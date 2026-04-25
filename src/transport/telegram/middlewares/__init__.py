from aiogram import Router

from .base import EventTypedMiddleware
from .error import ErrorMiddleware
from .garbage import GarbageMiddleware
from .user import UserMiddleware


def setup_middlewares(router: Router) -> None:
    """Setup all middlewares for the Telegram router."""
    outer_middlewares: list[EventTypedMiddleware] = [
        UserMiddleware(),
        ErrorMiddleware(),
    ]

    inner_middlewares: list[EventTypedMiddleware] = [
        GarbageMiddleware(),
    ]

    for middleware in outer_middlewares:
        middleware.setup_outer(router=router)

    for middleware in inner_middlewares:
        middleware.setup_inner(router=router)


__all__ = ["setup_middlewares"]
