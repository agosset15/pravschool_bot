from sqlalchemy import Column, ForeignKey, Integer, VARCHAR

from bot.models.db import DatabaseModel, TimeStampMixin


class Code(DatabaseModel, TimeStampMixin):
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    text = Column(VARCHAR(255), nullable=False, primary_key=True)
    amount = Column(Integer)
    worker_id = Column(ForeignKey("workers.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    activations = Column(Integer)
