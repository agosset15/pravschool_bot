from typing import Annotated, Optional

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Header, HTTPException

from src.core.dto import UserDto
from src.services.bot import BotService
from src.services.user import UserService


@inject
async def get_user_from_request(
    bot_service: FromDishka[BotService],
    user_service: FromDishka[UserService],
    authorization: Annotated[Optional[str], Header()] = None,
) -> Optional[UserDto]:
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header is required")

    parts = authorization.split(" ", 1)
    if len(parts) != 2:
        raise HTTPException(status_code=401, detail="Invalid authorization format")

    auth_type, auth_data = parts

    if auth_type.lower() != "tma":
        raise HTTPException(status_code=401, detail="Unsupported authorization type")

    try:
        init_data = bot_service.validate_webapp_data(auth_data)
    except ValueError:
        raise HTTPException(status_code=401, detail="WebApp data invalid")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid init data: {str(e)}")

    if not init_data.user:
        raise HTTPException(status_code=401, detail="WebApp data invalid")
    user = await user_service.get(init_data.user.id)
    if not user:
        return await user_service.create(init_data.user)
    return user
