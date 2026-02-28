from typing import Optional

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import HTTPException, Request

from src.core.dto import UserDto
from src.services.bot import BotService
from src.services.user import UserService


@inject
async def get_user_from_request(
        request: Request,
        bot_service: FromDishka[BotService],
        user_service: FromDishka[UserService],
        raw: bool = False
) -> Optional[UserDto] | int:
    auth_data = (await request.json()).get("_auth", None)
    if not auth_data:
        raise HTTPException(status_code=401, detail="WebApp data invalid")
    user_id = bot_service.parse_and_validate_webapp_data(auth_data)
    if not user_id:
        raise HTTPException(status_code=401, detail="WebApp data invalid")
    user = await user_service.get(user_id)
    if not user:
        if raw:
            return user_id
        raise HTTPException(status_code=404, detail="User not found")
    return user
