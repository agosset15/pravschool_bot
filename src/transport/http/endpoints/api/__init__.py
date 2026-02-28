from .homework import router as homework_router
from .ns import router as ns_router
from .schedule import router as schedule_router
from .user import router as user_router

routers = (
    homework_router,
    ns_router,
    schedule_router,
    user_router,
)

__all__ = [
    "routers",
]
