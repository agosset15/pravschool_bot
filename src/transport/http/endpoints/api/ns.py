from datetime import date, timedelta
from typing import Annotated, List, Optional
from urllib.parse import unquote

from aiogram import Bot
from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from fastapi.responses import JSONResponse

from src.core.dto import UserDto
from src.core.exceptions import (
    AuthError,
    NetSchoolAPIError,
    NetSchoolError,
    NoResponseFromServerError,
)
from src.core.utils import date_now, json
from src.services.netschool import NetSchoolService
from src.transport.http.schemas.ns import (
    AssignmentInfoResponse,
    AttachmentRequest,
    DiaryResponse,
    ListStudentsResponse,
    ReportInitData,
    ReportRequest,
    StudentsResponse,
    WeeksResponse,
)
from src.transport.http.utils import get_user_from_request

router = APIRouter(prefix="/ns", tags=["netschool"])


@router.post("/send_attachment")
@inject
async def get_attachment_file(
    body: AttachmentRequest,
    user: Annotated[UserDto, Depends(get_user_from_request)],
    bot: FromDishka[Bot],
    netschool_service: FromDishka[NetSchoolService],
) -> JSONResponse:
    try:
        file, caption = await netschool_service.get_attachment(
            user, body.student_id, body.assignment_id, body.attachment_id
        )
    except AuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except NoResponseFromServerError:
        raise HTTPException(status_code=504, detail="Сервер электронного журнала не отвечает")
    await bot.send_document(user.telegram_id, file, caption=caption)
    return JSONResponse(status_code=200, content={"ok": True})


@router.get("/report/init", response_model=ReportInitData)
@inject
async def report_init(
    netschool_service: FromDishka[NetSchoolService],
    user: Annotated[UserDto, Depends(get_user_from_request)],
    student_id: Annotated[Optional[int], Query(description="ID ученика")] = None,
) -> ReportInitData:
    try:
        response = await netschool_service.get_report_filters(user, student_id)
    except NetSchoolAPIError as e:
        raise HTTPException(status_code=502, detail=str(e))
    return ReportInitData.model_validate(response)


@router.get("/report")
@inject
async def get_report(
    user: Annotated[UserDto, Depends(get_user_from_request)],
    query: Annotated[ReportRequest, Query()],
    netschool_service: FromDishka[NetSchoolService],
) -> JSONResponse:
    filters = json.decode(unquote(query.filters))
    try:
        report = await netschool_service.get_report(user, query.student_id, query.id, filters)
    except AuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except NoResponseFromServerError:
        raise HTTPException(status_code=504, detail="Сервер электронного журнала не отвечает")
    return JSONResponse(report)


@router.get("/comment/{payload}", response_model=AssignmentInfoResponse)
@inject
async def get_info(
    payload: Annotated[str, Path(..., description="Формат: assignment_id-student_id")],
    user: Annotated[UserDto, Depends(get_user_from_request)],
    netschool_service: FromDishka[NetSchoolService],
) -> JSONResponse:
    data = [int(x) for x in payload.split("-")]
    if not len(data) == 2:
        raise HTTPException(status_code=400, detail="Неверный формат данных")
    assignment_id, student_id = data
    try:
        info = await netschool_service.get_info(user, student_id, assignment_id)
        if not info:
            raise HTTPException(status_code=404, detail="Не найдены данные")
        assignment = await netschool_service.find_assignment(
            user, student_id, assignment_id, info.date, info.subject.id
        )
        if not assignment:
            raise HTTPException(status_code=404, detail="Не найдены данные")
    except AuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except NoResponseFromServerError:
        raise HTTPException(status_code=504, detail="Сервер электронного журнала не отвечает")
    except NetSchoolError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return JSONResponse({"assignment": assignment.model_dump(), "details": info.model_dump()})


@router.get("/weeks", response_model=WeeksResponse)
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
    return JSONResponse({"weeks": weeks, "start": now.isoformat(), "end": end.isoformat()})


@router.get("/students", response_model=List[StudentsResponse])
@inject
async def get_students(
    user: Annotated[UserDto, Depends(get_user_from_request)],
    netschool_service: FromDishka[NetSchoolService],
) -> List[StudentsResponse]:
    try:
        students = await netschool_service.get_students(user)
    except AuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except NoResponseFromServerError:
        raise HTTPException
    return ListStudentsResponse.validate_python(students, from_attributes=True)


@router.get("/diary", response_model=DiaryResponse)
@inject
async def get_diary(
    student_id: Annotated[int, Query()],
    start: Annotated[str, Query(pattern=r"^\d{4}-\d{2}-\d{2}$")],
    end: Annotated[str, Query(pattern=r"^\d{4}-\d{2}-\d{2}$")],
    user: Annotated[UserDto, Depends(get_user_from_request)],
    netschool_service: FromDishka[NetSchoolService],
) -> DiaryResponse:
    try:
        diary = await netschool_service.get_diary(
            user, student_id, date.fromisoformat(start), date.fromisoformat(end)
        )
    except AuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except NoResponseFromServerError:
        raise HTTPException(status_code=504, detail="Сервер электронного журнала не отвечает")
    return DiaryResponse.model_validate(diary, from_attributes=True)
