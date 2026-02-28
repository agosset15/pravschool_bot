from dishka import Provider, Scope, provide

from src.services.bot import BotService
from src.services.broadcast import BroadcastService
from src.services.netschool import NetSchoolApiFactory, NetSchoolService
from src.services.notification import NotificationService
from src.services.schedule import ScheduleService
from src.services.schedules_extra import SchedulesExtraService
from src.services.user import UserService
from src.services.webhook import WebhookService


class ServicesProvider(Provider):
    scope = Scope.APP

    bot = provide(source=BotService)
    notification = provide(source=NotificationService, scope=Scope.REQUEST)
    user = provide(source=UserService, scope=Scope.REQUEST)
    webhook = provide(source=WebhookService)
    broadcast = provide(source=BroadcastService, scope=Scope.REQUEST)
    netschool_api_factory = provide(source=NetSchoolApiFactory)
    netschool = provide(source=NetSchoolService, scope=Scope.REQUEST)
    schedules_extra = provide(source=SchedulesExtraService, scope=Scope.REQUEST)
    schedule = provide(source=ScheduleService, scope=Scope.REQUEST)