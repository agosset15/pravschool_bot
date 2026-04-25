from typing import Annotated

from cfgv import Optional
from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse

from src.core.dto import UserDto
from src.services.netschool import NetSchoolService
from src.services.schedule import ScheduleService
from src.services.user import UserService
from src.transport.http.schemas.user import UserCreateRequest, UserResponse, UserUpdateRequest
from src.transport.http.utils import get_user_from_request

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/", response_model=UserResponse)
@inject
async def get_user(
    user: Annotated[Optional[UserDto], Depends(get_user_from_request)],
) -> UserResponse | RedirectResponse:
    if not user:
        return RedirectResponse("/register")
    return UserResponse.model_validate(user, from_attributes=True)


@router.get("/count")
@inject
async def get_users_count(user_service: FromDishka[UserService]) -> int:
    return await user_service.count()


@router.post("/")
@inject
async def edit_user(
    user: Annotated[Optional[UserDto], Depends(get_user_from_request)],
    body: UserUpdateRequest,
    user_service: FromDishka[UserService],
    netschool_service: FromDishka[NetSchoolService],
) -> JSONResponse:
    if body.grade:
        user.grade = body.grade
    if body.login:
        user.login = body.login
    if body.password:
        await netschool_service.register(user, body.password)
    if body.default_child:
        user.default_child = body.default_child
    await user_service.update(user)
    return JSONResponse({"ok": True})


@router.post("/register")
@inject
async def register_user(
    body: UserCreateRequest,
    user: Annotated[Optional[UserDto], Depends(get_user_from_request)],
    schedule_service: FromDishka[ScheduleService],
    netschool_service: FromDishka[NetSchoolService],
) -> JSONResponse:
    schedule = await schedule_service.get(body.schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    user.grade = schedule.grade
    user.is_teacher = body.is_teacher
    user.schedule_id = schedule.id
    user.login = body.login
    success = await netschool_service.register(user, body.password)

    return JSONResponse({"ok": success}, status_code=(200 if success else 400))
