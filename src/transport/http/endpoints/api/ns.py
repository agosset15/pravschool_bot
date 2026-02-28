from datetime import date, datetime, timedelta
from typing import Annotated

from aiogram import Bot
from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request
from fastapi.responses import JSONResponse

from src.core.dto import UserDto
from src.core.exceptions import AuthError, NetSchoolAPIError, NoResponseFromServerError
from src.core.utils import date_now
from src.services.netschool import NetSchoolService
from src.transport.http.utils import get_user_from_request

router = APIRouter(prefix="/ns")

@router.post("/send_attachment")
@inject
async def get_attachment_file(
        user: Annotated[UserDto, Depends(get_user_from_request)],
        request: Request,
        bot: FromDishka[Bot],
        netschool_service: FromDishka[NetSchoolService]
) -> JSONResponse:
    data = await request.json()
    try:
        file, caption = await netschool_service.get_attachment(
            user, data["student_id"], data["assignment_id"], data["attachment_id"]
        )
    except AuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except NoResponseFromServerError:
        raise HTTPException(status_code=504, detail="Сервер электронного журнала не отвечает")
    await bot.send_document(user.telegram_id, file, caption=caption)
    return JSONResponse(status_code=200, content={"ok": True})


@router.get("/report/init")
@inject
async def report_init(
        user: Annotated[UserDto, Depends(get_user_from_request)],
        request: Request,
        netschool_service: FromDishka[NetSchoolService]
) -> JSONResponse:
    data = await request.json()
    try:
        response = await netschool_service.get_report_filters(user, data.get("student_id", None))
    except NetSchoolAPIError as e:
        raise HTTPException(status_code=502, detail=str(e))
    return JSONResponse(status_code=200, content={"ok": True, "reports": response})


@router.get("/ns/report")
@inject
async def get_report(
        user: Annotated[UserDto, Depends(get_user_from_request)],
        request: Request,
        netschool_service: FromDishka[NetSchoolService]
) -> JSONResponse:
    data = await request.json()
    report_id = data.get("id")
    student_id = data.get("student_id")
    filters = data.get("filters", None)
    try:
        report = await netschool_service.get_report(user, student_id, report_id, filters)
    except AuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except NoResponseFromServerError:
        raise HTTPException(status_code=504, detail="Сервер электронного журнала не отвечает")
    return JSONResponse(report)


@router.get("/comment/{payload}")
@inject
async def get_info(
        payload: Annotated[str, Path(
            ...,
            description="Формат: year$month$day$lesson_id$assignment_id$student_id"
        )],
        user: Annotated[UserDto, Depends(get_user_from_request)],
        netschool_service: FromDishka[NetSchoolService]
) -> JSONResponse:
    data = [int(x) for x in payload.split("$")]
    d = date(data.pop(0), data.pop(0), data.pop(0))

    try:
        assignment, info = await netschool_service.get_info(
            user, data.pop(-1), d, data.pop(0), data.pop(0)
        )
    except AuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except NoResponseFromServerError:
        raise HTTPException(status_code=504, detail="Сервер электронного журнала не отвечает")

    return JSONResponse({"ok": True, "assignment": assignment, "details": info})


@router.get("/weeks")
async def get_weekdays() -> JSONResponse:
    now = date_now()
    year = now.year if now.month >= 9 else now.year - 1
    mon = date(year=year, month=9, day=1)
    if mon.weekday() != 0:
        mon = mon - timedelta(days=mon.weekday())
    sun = mon + timedelta(days=6)
    weeks = [[mon.strftime("%Y-%m-%d"), sun.strftime("%Y-%m-%d")]]
    start = mon
    while True:
        mon = mon + timedelta(weeks=1)
        sun = sun + timedelta(weeks=1)
        weeks.append([mon.strftime("%Y-%m-%d"), sun.strftime("%Y-%m-%d")])
        if sun >= date(
            start.year + 1, (start - timedelta(days=1)).month, (start - timedelta(days=1)).day
        ):
            break
    if now.weekday() != 0:
        now = now - timedelta(days=now.weekday())
    end = now + timedelta(days=6)
    return JSONResponse({"ok": True, "weeks": weeks, "start": now, "end": end})


@router.get("/diary")
@inject
async def get_diary(
        student_id: Annotated[int, Query(...)],
        start: Annotated[str, Query(..., pattern=r"^\d{4}-\d{2}-\d{2}$")],
        end: Annotated[str, Query(..., pattern=r"^\d{4}-\d{2}-\d{2}$")],
        user: Annotated[UserDto, Depends(get_user_from_request)],
        netschool_service: FromDishka[NetSchoolService]
) -> JSONResponse:
    try:
        diary = await netschool_service.get_diary(
            user, student_id,datetime.strptime(start, "%Y-%m-%d"),datetime.strptime(end, "%Y-%m-%d")  # noqa: DTZ007
        )
    except AuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except NoResponseFromServerError:
        raise HTTPException(status_code=504, detail="Сервер электронного журнала не отвечает")
    return JSONResponse({"ok": True, "diary": diary})
