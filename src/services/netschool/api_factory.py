from src.core.dto import UserDto
from src.core.utils import json
from src.infrastructure.cache.keys import NetschoolSessionDataKey
from src.infrastructure.http import NetSchoolAPI
from src.services.base import BaseService


class NetSchoolApiFactory(BaseService):
    async def create(self, user: UserDto) -> NetSchoolAPI:
        assert user.login and user.password
        session_data_key = NetschoolSessionDataKey(login=user.login)
        session_data_raw = await self.redis.get(self.retort.dump(session_data_key))
        session_data = json.decode(session_data_raw) if session_data_raw else None

        api = NetSchoolAPI(
            url=self.config.netschool.url,
            username=user.login,
            password=user.password,
            student_id=user.default_child,
            school_id=self.config.netschool.school_id,
        )

        if not session_data:
            await api.login()
        else:
            await api.set_session_data(session_data)

        session_data = api.get_session_data()
        await self.redis.set(self.retort.dump(session_data_key), json.encode(session_data))
        return api

    async def update_session_data(self, api: NetSchoolAPI) -> None:
        session_data_key = NetschoolSessionDataKey(login=api.username)
        session_data = api.get_session_data()
        await self.redis.set(self.retort.dump(session_data_key), json.encode(session_data))

    async def delete_all_session_data(self) -> None:
        session_data_key = NetschoolSessionDataKey(login="*")
        keys = await self.redis.keys(self.retort.dump(session_data_key))
        await self.redis.delete(*keys)