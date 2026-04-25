from aiogram.filters import BaseFilter
from aiogram.types import InlineQuery


class InlineGradesFilter(BaseFilter):
    async def __call__(self, event: InlineQuery, grades: list[str]) -> bool:
        return event.query in grades
