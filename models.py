from enum import Enum
from datetime import date, datetime
from typing import List, Optional
import uuid
from database import Base
from sqlalchemy import Column, Date, DateTime, Integer, String, Boolean, ForeignKey, JSON, Enum as SQLEnum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from schemas import Prediction


class LanguageEnum(str, Enum):
    ENGLISH = "en"
    YORUBA = "yo"
    IGBO = "ig"
    HAUSA = "ha"


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[str] = mapped_column(nullable=False)
    phone_number: Mapped[str] = mapped_column(nullable=False)
    is_verified:  Mapped[bool] = mapped_column(Boolean, default=False)
    language_preference: Mapped[LanguageEnum] = mapped_column(
        SQLEnum(LanguageEnum),
        default=LanguageEnum.ENGLISH,
        nullable=False
    )

    profile: Mapped["UserProfile"] = relationship(
        "UserProfile", back_populates="user", uselist=False, cascade="all, delete")
    cycle: Mapped["Cycles"] = relationship(
        "Cycles", back_populates="user", uselist=False, cascade="all, delete")
    insights: Mapped["Insights"] = relationship(
        "Insights", back_populates="user", uselist=False, cascade="all, delete")
    

class PendingUser(Base):
    __tablename__ = "pending_users"

    id = Column(Integer, primary_key=True, index=True)

    phone_number = Column(String, nullable=False, index=True)
    email = Column(String, nullable=False)
    username = Column(String, nullable=False)

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)

    language_preference = Column(
        SQLEnum(LanguageEnum),
        default=LanguageEnum.ENGLISH,
        nullable=False
    )

    expires_at = Column(DateTime, nullable=False)


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), unique=True)

    age = Column(Integer)
    cycle_length = Column(Integer)
    last_period_date = Column(Date)
    ttc_history = Column(String)
    faith_preference = Column(String)
    audio_preference = Column(Boolean)

    user = relationship("Users", back_populates="profile")


class OTP(Base):
    __tablename__ = "otp"

    id = Column(Integer, primary_key=True, index=True)
    verification_id = Column(
        String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    phone = Column(String, nullable=False)
    otp_hashed = Column(String, nullable=False) 
    attempts = Column(Integer, default=0)
    is_used = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=False)


class CashedTranslations(Base):
    __tablename__ = "cached_translations"

    id = Column(Integer, primary_key=True, index=True)
    Original_text = Column(Text,  nullable=False)
    translated_text = Column(Text,  nullable=False)
    language = Column(String(10), nullable=False)


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
    user_id: Mapped[int] = mapped_column(ForeignKey(
        "users.id", ondelete="CASCADE"), unique=True)

    next_period: Mapped[date] = mapped_column(Date, nullable=False)
    ovulation_day: Mapped[date] = mapped_column(Date, nullable=False)
    fertile_period_start: Mapped[date] = mapped_column(Date, nullable=False)
    fertile_period_end: Mapped[date] = mapped_column(Date, nullable=False)

    symptoms: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    insight_text: Mapped[str] = mapped_column(Text, nullable=False)

    user: Mapped["Users"] = relationship("Users", back_populates="insights")
