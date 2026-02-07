from typing import List
from sqlalchemy import Boolean, Column, Integer, String, ARRAY, ForeignKey
from sqlalchemy.orm import relationship, Mapped

from bot.models.db import TimeStampMixin, DatabaseModel, ChatIdMixin


class City(DatabaseModel):
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    name = Column(String)
    whores: Mapped[List["Whore"]] = relationship(back_populates="city")


class CityRelatedModel(DatabaseModel):
    __abstract__ = True

    city_id = Column(
        ForeignKey("citys.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )


class Whore(CityRelatedModel, TimeStampMixin):
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    name = Column(String)
    photos = Column(ARRAY(String))
    cost_1 = Column(Integer)
    cost_3 = Column(Integer)
    cost_night = Column(Integer)
    age = Column(Integer)
    height = Column(Integer)
    boobs = Column(Integer)
    worker_id = Column(ForeignKey('workers.id', ondelete="SET NULL"), nullable=True)
    user_id = Column(Integer, nullable=True)
    city: Mapped["City"] = relationship(back_populates="whores")
