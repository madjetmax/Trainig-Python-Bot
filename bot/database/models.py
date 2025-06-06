from sqlalchemy import DateTime, Float, String, Text, Boolean, Integer, JSON, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column,  relationship
from typing import List
from config import * 

import datetime
from zoneinfo import ZoneInfo



base_time_zone = ZoneInfo(MODELS_TIME_ZONE)

def now() -> datetime.datetime:
    return datetime.datetime.now(base_time_zone)

class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime(True), default=now())
    updated: Mapped[DateTime] = mapped_column(DateTime(True), default=now(), onupdate=now())
    
class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(Text)

    trainings: Mapped["UserTrainings"] = relationship(back_populates="user")
    finished_trainings: Mapped[List["FinishedUserTraining"]] = relationship(back_populates="user")

    aura: Mapped[int] = mapped_column(Integer, default=0)

    def __str__(self):
        data = f"{self.id}, {self.name}, {self.status}, {self.aura}"
        return data
    
class UserTrainings(Base):
    __tablename__ = "user_trainings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="trainings")

    days_data: Mapped[dict] = mapped_column(JSON)

    time_start_hours: Mapped[int] = mapped_column(Integer)
    time_start_minutes: Mapped[int] = mapped_column(Integer)

class FinishedUserTraining(Base):
    __tablename__ = "finished_user_trainings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # for related user
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="finished_trainings")

    # training data
    body_part: Mapped[str] = mapped_column(String(100), nullable=True)
    full_training_data: Mapped[dict] = mapped_column(JSON, default={}, nullable=False) # idk but maybe i will need this

    all_reps_count: Mapped[int] = mapped_column(Integer)
    reps_finished: Mapped[int] = mapped_column(Integer)

    time_start: Mapped[DateTime] = mapped_column(DateTime(True))
    full_training_time: Mapped[str] = mapped_column(String(20))
    time_end: Mapped[DateTime] = mapped_column(DateTime(True))

    aura_got: Mapped[int] = mapped_column(Integer)