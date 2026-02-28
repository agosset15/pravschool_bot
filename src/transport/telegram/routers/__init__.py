from aiogram import Router

from . import dashboard, extra, homework, menu, netschool


def setup_routers(router: Router) -> None:
    # WARNING: The order of router registration matters!
    routers = [
        extra.notification.router,
        extra.user_updates.router,
        extra.goto.router,
        extra.inline.router,
        extra.netschool_input.router,
        extra.schedule_input.router,
        #
        menu.handlers.router,
        menu.dialog.router,
        #
        netschool.dialog.router,
        #
        homework.dialog.router,
        #
        dashboard.dialog.router,
        #
        dashboard.users.dialog.router,
        dashboard.users.user.dialog.router,
    ]

    router.include_routers(*routers)