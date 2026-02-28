from typing import Any, Optional
from uuid import UUID

from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.enums import BroadcastAudience, BroadcastMessageStatus, BroadcastStatus

from .base import BaseSql
from .timestamp import TimestampMixin


class Broadcast(BaseSql, TimestampMixin):
    __tablename__ = "broadcasts"

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[UUID] = mapped_column(unique=True)

    status: Mapped[BroadcastStatus] = mapped_column(index=True)
    audience: Mapped[BroadcastAudience]

    total_count: Mapped[int]
    success_count: Mapped[int]
    failed_count: Mapped[int]

    payload: Mapped[dict[str, Any]]

    messages: Mapped[list["BroadcastMessage"]] = relationship(
        back_populates="broadcast",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class BroadcastMessage(BaseSql):
    __tablename__ = "broadcast_messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    broadcast_id: Mapped[int] = mapped_column(
        ForeignKey("broadcasts.id", ondelete="CASCADE"),
        index=True,
    )

    user_telegram_id: Mapped[int] = mapped_column(BigInteger, index=True)
    message_id: Mapped[Optional[int]] = mapped_column(BigInteger)

    status: Mapped[BroadcastMessageStatus] = mapped_column(index=True)

    broadcast: Mapped["Broadcast"] = relationship(back_populates="messages")