from typing import Type, TypeVar, List, AsyncIterator, Callable

from sqlalchemy import select, update, delete, Result, func
from sqlalchemy.orm import joinedload
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.models.base import *

T = TypeVar("T", User, Schedule, Homework, Day, Lesson)


class DefaultService:
    def __init__(self, session: Callable[[], AsyncIterator[AsyncSession]]):
        self.session = session

    async def create(self, table: Type[T], **values) -> int:
        insert_stmt = insert(
            table
        ).values(
            **values
        ).returning(table.id)
        async with self.session() as session:
            result = await session.execute(insert_stmt)
            await session.commit()
        return result.scalars().first()

    async def get_one(self, table: Type[T], *clauses, joined=None) -> T:
        statement = select(table).where(*clauses)
        if joined:
            statement = statement.options(joinedload(joined))
        async with self.session() as session:
            result: Result = await session.execute(statement)
        return result.scalars().first()

    async def get_all(self, table: Type[T], *clauses, ordered=None, joined=None, having=None) -> List[T]:
        statement = select(table).where(*clauses)
        if ordered:
            statement = statement.order_by(ordered)
        if joined:
            statement = statement.options(joinedload(joined))
        if having:
            statement = statement.group_by(table.id).join(having[0]).having(func.count(having[1]) > 0)
        async with self.session() as session:
            result: Result = await session.execute(statement)
        return list(result.scalars().all())

    async def update(self, table: Type[T], *clauses, **values) -> None:
        statement = update(
            table
        ).where(
            *clauses
        ).values(
            **values
        )
        async with self.session() as session:
            await session.execute(statement)
            await session.commit()

    async def delete(self, table: Type[T], *clauses) -> None:
        statement = delete(
            table
        ).where(
            *clauses
        )
        async with self.session() as session:
            await session.execute(statement)
            await session.commit()

    async def count(self, table: Type[T], *clauses) -> int:
        statement = select(table).where(*clauses)
        async with self.session() as session:
            result: Result = await session.execute(statement)
        return len(result.scalars().fetchall())
