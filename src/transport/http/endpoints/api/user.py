from typing import Annotated

from cfgv import Optional
from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse

from src.core.dto import UserDto
from src.core.enums import ScheduleType
from src.services.bot import BotService
from src.services.netschool import NetSchoolService
from src.services.schedule import ScheduleService
from src.services.user import UserService
from src.transport.http.schemas.user import UserResponse
from src.transport.http.utils import get_user_from_request

router = APIRouter(prefix="/user")

@router.get("/", response_model=UserResponse)
@inject
async def getdb_user(
        user: Annotated[Optional[UserDto], Depends(get_user_from_request)]
) -> UserResponse | RedirectResponse:
    if not user:
        return RedirectResponse("/register")
    return UserResponse.model_validate(user)


@router.get("/count")
@inject
async def getdb_user_count(user_service: FromDishka[UserService]) -> int:
    return await user_service.count()

@router.post("/class")
@inject
async def edit_db_class(
        user: Annotated[Optional[UserDto], Depends(get_user_from_request)],
        request: Request,
        user_service: FromDishka[UserService]
) -> JSONResponse:
    data = await request.json()
    grade = data.get("grade", None)
    if not grade:
        return JSONResponse({"ok": False, "error": "No grade provided"}, status_code=400)
    user.grade = grade
    await user_service.update(user)
    return JSONResponse({"ok": True})


@router.post("/ns")
@inject
async def edit_db_ns(
        user: Annotated[Optional[UserDto], Depends(get_user_from_request)],
        request: Request,
        netschool_service: FromDishka[NetSchoolService]
) -> JSONResponse:
    data = await request.json()
    success = await netschool_service.register(user, data["password"])

    return JSONResponse({"ok": success}, status_code=(200 if success else 400))


@router.post("/register")
@inject
async def register_user(
        request: Request,
        bot_service: FromDishka[BotService],
        user_service: FromDishka[UserService],
        schedule_service: FromDishka[ScheduleService],
        netschool_service: FromDishka[NetSchoolService]
) -> JSONResponse:
    data = await request.json()
    user_init = bot_service.validate_webapp_data(data["_auth"]).user
    if not user_init:
        raise HTTPException(status_code=401, detail="Invalid webapp data")
    user_db = await user_service.get(user_init.id)
    if user_db:
        raise HTTPException(status_code=406, detail="Authorized")
    user = await user_service.create(user_init)
    schedule = (await schedule_service.find_by_type_partial_grade(
        ScheduleType.TEACHER if data["is_teacher"] == "true" else ScheduleType.COMMON,
        data["grade"]
    ))[0]
    user.grade= data["grade"]
    user.is_teacher= data["is_teacher"]
    user.schedule_id = schedule.id
    user.login=data["ns_uname"]
    success = await netschool_service.register(user, data["password"])

    return JSONResponse({"ok": success}, status_code=(200 if success else 400))
