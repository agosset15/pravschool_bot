from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from tg_bot.models.db import Base, TimeStampMixin, Int32


class Photo(Base, TimeStampMixin):
    id: Mapped[Int32] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(length=15), primary_key=True)
    file_id: Mapped[str] = mapped_column(String(length=255))
