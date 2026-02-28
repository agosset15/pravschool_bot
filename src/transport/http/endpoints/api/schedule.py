from datetime import timedelta
from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fluentogram import TranslatorRunner

from src.core.dto import UserDto
from src.core.enums import ScheduleType, WeekDay
from src.core.utils import datetime_now
from src.services.schedule import ScheduleService
from src.services.user import UserService
from src.transport.http.schemas.schedule import ScheduleResponse
from src.transport.http.utils import get_user_from_request

router = APIRouter(prefix="/schedule")

@router.get("/today")
@inject
async def get_schedule_today(
        request: Request,
        user_service: FromDishka[UserService],
        i18n: FromDishka[TranslatorRunner]
) -> JSONResponse:
    user_telegram_id = (await request.json()).get("tgid")
    user = await user_service.get(user_telegram_id)
    if user is None:
        raise HTTPException(
            status_code=401, detail="Вы не зарегистрированы в боте. Проверьте id на опечатки."
        )

    now = datetime_now()
    day_label = i18n.get("today")
    weekday = now.weekday()

    if now.hour > 14:
        weekday = (now + timedelta(days=1)).weekday()
        day_label = i18n.get("tomorrow")

    if weekday > 4:
        return JSONResponse(
            {
                "rasp": i18n.get("weekend"),
                "tomorrow": f"{day_label} {WeekDay(weekday).get_text(i18n)}"
            },
            status_code=200
        )

    schedule = await user_service.get_schedule(user)
    if schedule is None:
        raise HTTPException(
            status_code=404, detail="Расписание не найдено. Проверьте id на опечатки."
        )
    return JSONResponse(
        {
        "rasp": "<br />".join(schedule.days[weekday].lessons_text),
        "tomorrow": f"{day_label} {WeekDay(weekday).get_text(i18n)}"
        },
        status_code=200
    )


@router.get("/", response_model=ScheduleResponse)
@inject
async def get_schedule(
        user: Annotated[UserDto, Depends(get_user_from_request)],
        user_service: FromDishka[UserService]
) -> ScheduleResponse:
    schedule = await user_service.get_schedule(user)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return ScheduleResponse.model_validate(schedule)


@router.get("/schedule/rooms", response_model=ScheduleResponse)
@inject
async def get_rooms_schedule(
        schedule_service: FromDishka[ScheduleService]
) -> ScheduleResponse:
    schedule = await schedule_service.get_all_by_type(ScheduleType.ROOM)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return ScheduleResponse.model_validate(schedule)
