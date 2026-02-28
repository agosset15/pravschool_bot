from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Path
from fastapi.responses import JSONResponse

from src.services.schedule import ScheduleService

router = APIRouter(prefix="/homework")

@router.get("/homework/{day_id}")
@inject
async def getdb_homework(
        day_id: Annotated[int, Path(..., description="ID дня")],
        schedule_service: FromDishka[ScheduleService]
) -> JSONResponse:
    homeworks = await schedule_service.parse_homeworks(day_id)

    text = "<br />".join(homeworks)
    return JSONResponse({"ok": True, "hw": text})
