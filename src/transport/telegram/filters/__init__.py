from aiogram import Router

from .private import PrivateFilter

__all__ = [
    "setup_global_filters",
]


def setup_global_filters(router: Router) -> None:
    filters = [
        PrivateFilter(),  # global filter allows only private chats
    ]

    for f in filters:
        router.message.filter(f)