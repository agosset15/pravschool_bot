from typing import Any, Optional, Type, TypeVar, Union

from sqlalchemy import ColumnExpressionArgument, delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute, QueryableAttribute, joinedload

from src.infrastructure.db.models import BaseSql

T = TypeVar("T", bound=BaseSql)
ModelType = Type[T]

ConditionType = ColumnExpressionArgument[Any]
OrderByArgument = Union[ColumnExpressionArgument[Any], InstrumentedAttribute[Any]]
ColumnAttribute = QueryableAttribute[Any]


class BaseRepository:
    session: AsyncSession

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_instance(self, instance: T) -> T:
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def create_instances(self, instances: list[T]) -> list[T]:
        if not instances:
            return []

        self.session.add_all(instances)
        await self.session.flush()
        for instance in instances:
            await self.session.refresh(instance)
        return instances

    async def merge_instance(self, instance: T) -> T:
        return await self.session.merge(instance)

    async def delete_instance(self, instance: T) -> None:
        await self.session.delete(instance)

    async def _get_one(
            self,
            model: ModelType,
            *conditions: ConditionType,
            joined: Optional[ColumnAttribute] = None,
            limit: Optional[int] = None) -> Optional[T]:
        stmt = select(model).where(*conditions)
        if joined:
            stmt = stmt.options(joinedload(joined))
        if limit:
            stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def _get_many(
        self,
        model: ModelType,
        *conditions: ConditionType,
        order_by: Optional[OrderByArgument] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> list[T]:
        query = select(model).where(*conditions)

        if order_by is not None:
            if isinstance(order_by, (list, tuple)):
                query = query.order_by(*order_by)  # type: ignore[invalid-argument-type]
            else:
                query = query.order_by(order_by)

        if limit is not None:
            query = query.limit(limit)

        if offset is not None:
            query = query.offset(offset)

        result = await self.session.execute(query)
        return list(result.unique().scalars().all())

    async def _update(
        self,
        model: ModelType,
        *conditions: ConditionType,
        load_result: bool = True,
        **kwargs: Any,
    ) -> Optional[T]:
        if not kwargs:
            return await self._get_one(model, *conditions) if load_result else None

        stmt = update(model).where(*conditions).values(**kwargs)

        if load_result:
            stmt = stmt.returning(model)
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()

        await self.session.execute(stmt)
        return None

    async def _delete(self, model: ModelType, *conditions: ConditionType) -> int:
        result = await self.session.execute(delete(model).where(*conditions))
        return result.rowcount  # type: ignore[attr-defined, no-any-return]

    async def _count(self, model: ModelType, *conditions: ConditionType) -> int:
        query = select(func.count()).select_from(model).where(*conditions)
        result = await self.session.scalar(query)
        return result or 0
