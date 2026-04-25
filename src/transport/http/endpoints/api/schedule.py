from datetime import timedelta
from typing import Annotated, List, Optional

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from fluentogram import TranslatorRunner

from src.core.dto import UserDto
from src.core.enums import ScheduleType, WeekDay
from src.core.utils import datetime_now
from src.services.schedule import ScheduleService
from src.services.user import UserService
from src.transport.http.schemas.schedule import (
    ListScheduleOnlyResponse,
    ScheduleOnlyResponse,
    ScheduleResponse,
)
from src.transport.http.utils import get_user_from_request

router = APIRouter(prefix="/schedule", tags=["schedule"])


@router.get("/today")
@inject
async def get_schedule_today(
    user_telegram_id: Annotated[Optional[int], Query(alias="tgid")],
    user_service: FromDishka[UserService],
    i18n: FromDishka[TranslatorRunner],
) -> JSONResponse:
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
                "tomorrow": f"{day_label} {WeekDay(weekday + 1).get_text(i18n)}",
            },
            status_code=200,
        )

    schedule = await user_service.get_schedule(user)
    if schedule is None:
        raise HTTPException(
            status_code=404, detail="Расписание не найдено. Проверьте id на опечатки."
        )
    return JSONResponse(
        {
            "rasp": "<br />".join(schedule.days[weekday].lessons_text),
            "tomorrow": f"{day_label} {WeekDay(weekday + 1).get_text(i18n)}",
        },
        status_code=200,
    )


@router.get("/", response_model=ScheduleResponse)
@inject
async def get_schedule(
    user: Annotated[UserDto, Depends(get_user_from_request)],
    user_service: FromDishka[UserService],
    schedule_service: FromDishka[ScheduleService],
    i18n: FromDishka[TranslatorRunner],
    schedule_id: Optional[int] = Query(None),
) -> ScheduleResponse:
    if schedule_id:
        schedule = await schedule_service.get(schedule_id)
    else:
        schedule = await user_service.get_schedule(user)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return ScheduleResponse.model_validate(
        schedule, from_attributes=True, context={"days": WeekDay.str_list(i18n)}
    )


@router.get("/grades", response_model=List[ScheduleOnlyResponse])
@inject
async def get_grades(schedule_service: FromDishka[ScheduleService]) -> List[ScheduleOnlyResponse]:
    grades = await schedule_service.get_all_by_type(ScheduleType.COMMON, with_days=False)
    if not grades:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return ListScheduleOnlyResponse.validate_python(grades, from_attributes=True)


@router.get("/teachers", response_model=List[ScheduleOnlyResponse])
@inject
async def get_teachers_schedule(
    schedule_service: FromDishka[ScheduleService],
) -> List[ScheduleOnlyResponse]:
    grades = await schedule_service.get_all_by_type(ScheduleType.TEACHER, with_days=False)
    if not grades:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return ListScheduleOnlyResponse.validate_python(grades, from_attributes=True)


@router.get("/rooms", response_model=List[ScheduleOnlyResponse])
@inject
async def get_rooms_schedule(
    schedule_service: FromDishka[ScheduleService],
) -> list[ScheduleOnlyResponse]:
    schedule = await schedule_service.get_all_by_type(ScheduleType.ROOM, with_days=True)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return ListScheduleOnlyResponse.validate_python(schedule, from_attributes=True)
