from sqlalchemy import DateTime, Float, String, Text, Boolean, ARRAY, Integer, JSON, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column,  relationship
from sqlalchemy.orm import joinedload

from typing import List
from config import * 
from .datatypes import CustomJSON
import datetime
from zoneinfo import ZoneInfo



base_time_zone = ZoneInfo(MODELS_TIME_ZONE)

def now() -> datetime.datetime:
    return datetime.datetime.now(base_time_zone)

class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime(True), default=now())
    updated: Mapped[DateTime] = mapped_column(DateTime(True), default=now(), onupdate=now())
    

# *user
class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(Text)

    lang: Mapped[str] = mapped_column(String(2), nullable=True, default="en")

    # relations
    trainings: Mapped["UserTrainings"] = relationship(back_populates="user", cascade="all, delete-orphan", passive_deletes=True)
    finished_trainings: Mapped[List["FinishedUserTraining"]] = relationship(back_populates="user", cascade="all, delete-orphan", passive_deletes=True)
    stats: Mapped[List["UserStats"]] = relationship(back_populates="user", cascade="all, delete-orphan", passive_deletes=True)
    
    admin_chatting: Mapped[List["AdminChatting"]] = relationship(back_populates="user", cascade="all, delete-orphan", passive_deletes=True)

    # aura
    aura: Mapped[float] = mapped_column(Float, default=0)

    def __str__(self):
        data = f"{self.id}, {self.name}, {self.status}, {self.aura}"
        return data
    
    
class UserTrainings(Base):
    __tablename__ = "user_trainings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    user: Mapped["User"] = relationship(back_populates="trainings")

    days_data: Mapped[dict] = mapped_column(CustomJSON)

    time_start_hours: Mapped[int] = mapped_column(Integer)
    time_start_minutes: Mapped[int] = mapped_column(Integer)

    all_body_parts: Mapped[list[str]] = mapped_column(CustomJSON, nullable=True) 
    all_reps_names: Mapped[list[str]] = mapped_column(CustomJSON, nullable=True) 


class FinishedUserTraining(Base):
    __tablename__ = "finished_user_trainings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # for related user
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    user: Mapped["User"] = relationship(back_populates="finished_trainings")

    # training data
    body_part: Mapped[str] = mapped_column(String(100), nullable=True)
    full_training_data: Mapped[dict] = mapped_column(CustomJSON, default={}, nullable=False) # idk but maybe i will need this

    all_reps_count: Mapped[int] = mapped_column(Integer)
    reps_finished: Mapped[int] = mapped_column(Integer)

    time_start: Mapped[DateTime] = mapped_column(DateTime(True))
    full_training_time: Mapped[str] = mapped_column(String(20))
    time_end: Mapped[DateTime] = mapped_column(DateTime(True))

    aura_got: Mapped[int] = mapped_column(Integer)

class UserStats(Base):
    __tablename__ = "user_stats"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    user: Mapped["User"] = relationship(back_populates="stats")

    # aura
    aura_reduced_on_training_skip: Mapped[int] = mapped_column(Integer, nullable=True)



# TODO bot and admin
class AdminChatting(Base):
    __tablename__ = "admin_chatting"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # for related user
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    user: Mapped["User"] = relationship(back_populates="admin_chatting")

    # data
    message: Mapped[str] = mapped_column(Text)
    photo_path: Mapped[str] = mapped_column(String(200), nullable=True) # user can send photo
    