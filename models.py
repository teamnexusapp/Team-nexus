from datetime import datetime
from typing import List, Optional
from database import Base
from sqlalchemy import Column, Date, DateTime, Integer, String, Boolean, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from schema import Prediction


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    username: Mapped[str] = mapped_column(
        String(40), unique=True, server_default="guest")
    first_name: Mapped[str]
    last_name: Mapped[str]
    hashed_password: Mapped[str]
    role: Mapped[str]
    phone_number: Mapped[str]

    profile: Mapped["UserProfile"] = relationship(
        "UserProfile", back_populates="user", uselist=False, cascade="all, delete")
    cycle: Mapped["Cycles"] = relationship(
        "Cycles", back_populates="user", uselist=False, cascade="all, delete")
    insights: Mapped["Insights"] = relationship(
        "Insights", back_populates="user", uselist=False, cascade="all, delete")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)

    age = Column(Integer)
    cycle_length = Column(Integer)
    last_period_date = Column(Date)
    ttc_history = Column(String)
    faith_preference = Column(String)
    language_preference = Column(String)
    audio_preference = Column(Boolean)

    user = relationship("Users", back_populates="profile")


class Cycles(Base):
    __tablename__ = "cycles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(
        "users.id", ondelete="CASCADE"), unique=True)

    last_period_date: Mapped[Date] = mapped_column(Date, nullable=False)
    cycle_length: Mapped[int] = mapped_column(Integer, default=28)
    period_length: Mapped[int] = mapped_column(Integer, default=5)

 
    symptoms: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)

    user: Mapped["Users"] = relationship("Users", back_populates="cycle")
    


class Insights(Base):
    __tablename__ = "insights"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)

    next_period: Mapped[Date] = mapped_column(Date, nullable=False)
    ovulation_day: Mapped[Date] = mapped_column(Date, nullable=False)
    fertile_period_start: Mapped[Date] = mapped_column(Date, nullable=False)
    fertile_period_end: Mapped[Date] = mapped_column(Date, nullable=False)

   
    symptoms: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    user: Mapped["Users"] = relationship("Users", back_populates="insights")


