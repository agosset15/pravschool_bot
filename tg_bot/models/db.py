from __future__ import annotations

import re
import contextlib
from datetime import datetime
from typing import Optional, Type, cast, Any, Dict, Pattern, Final, TypeAlias, Annotated, AsyncIterator

from sqlalchemy import String, TIMESTAMP, func, BigInteger, SmallInteger, Integer, DateTime
from sqlalchemy.orm import has_inherited_table, declared_attr, DeclarativeBase, registry, Mapped, mapped_column
from sqlalchemy.orm.decl_api import declarative_mixin
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.asyncio import (create_async_engine, AsyncSession, async_sessionmaker, AsyncAttrs, AsyncConnection,
                                    AsyncEngine)

from tg_bot.config import DB_PORT, DB_HOST, DB_USER, DB_DRIVER, DB_NAME, DB_PASSWORD

# Регулярное выражение, которое разделяет строку по заглавным буквам
TABLE_NAME_REGEX: Pattern[str] = re.compile(r"(?<=[A-Z])(?=[A-Z][a-z])|(?<=[^A-Z])(?=[A-Z])")
PLURAL: Final[str] = "s"


Int16: TypeAlias = Annotated[int, 16]
Int32: TypeAlias = Annotated[int, 32]
Int64: TypeAlias = Annotated[int, 64]


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True
    __mapper_args__ = {"eager_defaults": True}

    registry = registry(
        type_annotation_map={
            Int16: SmallInteger,
            Int32: Integer,
            Int64: BigInteger,
            datetime: DateTime(timezone=True),
        }
    )

    @declared_attr
    def __tablename__(self) -> Optional[str]:
        """
        Автоматически генерирует имя таблицы из названия модели, примеры:

        OrderItem -> order_items
        Order -> orders
        """
        if has_inherited_table(cast(Type[Base], self)):
            return None
        cls_name = cast(Type[Base], self).__qualname__
        table_name_parts = re.split(TABLE_NAME_REGEX, cls_name)
        formatted_table_name = "".join(
            table_name_part.lower() + "_" for i, table_name_part in enumerate(table_name_parts)
        )
        last_underscore = formatted_table_name.rfind("_")
        return formatted_table_name[:last_underscore] + PLURAL

    def _get_attributes(self) -> Dict[Any, Any]:
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

    def __str__(self) -> str:
        attributes = " | ".join(f'{k} = {v}' for k, v in self._get_attributes().items())
        return f"{self.__class__.__qualname__}({attributes})"


@declarative_mixin
class TimeStampMixin:
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_onupdate=func.now(),
                                                 server_default=func.now())


@declarative_mixin
class ChatIdMixin:
    __abstract__ = True

    chat_id: Mapped[Int64] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(length=255), nullable=False)
    username: Mapped[str] = mapped_column(String(length=255), nullable=True)


class DatabaseSessionManager:
    def __init__(self, echo=False) -> None:
        self._engine: Optional[AsyncEngine] = None
        self._sessionmaker: Optional[async_sessionmaker[AsyncSession]] = None
        self.echo = echo

    def init(self) -> None:
        # Just additional example of customization.
        # you can add parameters to init and so on
        if "postgresql" in DB_DRIVER:
            # These settings are needed to work with pgbouncer in transaction mode
            # because you can't use prepared statements in such case
            connect_args = {
                "statement_cache_size": 0,
                "prepared_statement_cache_size": 0,
            }
        else:
            connect_args = {}
        self._engine = create_async_engine(
            URL.create(
                drivername=DB_DRIVER,
                username=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                database=DB_NAME,
                port=DB_PORT
            ),
            query_cache_size=1200,
            pool_size=10,
            max_overflow=200,
            future=True,
            echo=self.echo,
            connect_args=connect_args,
        )
        self._sessionmaker = async_sessionmaker(bind=self._engine, expire_on_commit=False, class_=AsyncSession)

    async def close(self) -> None:
        if self._engine is None:
            return
        await self._engine.dispose()
        self._engine = None
        self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            raise IOError("DatabaseSessionManager is not initialized")
        async with self._sessionmaker() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise IOError("DatabaseSessionManager is not initialized")
        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise


db_manager = DatabaseSessionManager()
