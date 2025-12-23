from utils.enum import LanguageEnum, RoleEnum
from datetime import date, datetime
from typing import List, Optional
import uuid
from database import Base
from sqlalchemy import Column, Date, DateTime, Integer, String, Boolean, ForeignKey, JSON, Enum as SQLEnum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship






class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[RoleEnum] = mapped_column(
        SQLEnum(RoleEnum),
        default=RoleEnum.USER,
        nullable=False
    )
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





# class Users(Base):
#     __tablename__ = "users"

#     id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
#     email: Mapped[str] = mapped_column(unique=True, nullable=False)

#     username: Mapped[str] = mapped_column(unique=True, nullable=False)

#     first_name: Mapped[str] = mapped_column(nullable=False)
#     last_name: Mapped[str] = mapped_column(nullable=False)

#     hashed_password: Mapped[str | None] = mapped_column(nullable=True)

#     provider: Mapped[str] = mapped_column(default="local", nullable=False)
#     provider_id: Mapped[str | None] = mapped_column(unique=True, nullable=True)

#     role: Mapped[RoleEnum] = mapped_column(
#         SQLEnum(RoleEnum),
#         default=RoleEnum.USER,
#         nullable=False
#     )

#     phone_number: Mapped[str | None] = mapped_column(nullable=True)

#     is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

#     language_preference: Mapped[LanguageEnum] = mapped_column(
#         SQLEnum(LanguageEnum),
#         default=LanguageEnum.ENGLISH,
#         nullable=False
#     )

#     profile = relationship(
#         "UserProfile", back_populates="user", uselist=False, cascade="all, delete"
#     )
#     cycle = relationship(
#         "Cycles", back_populates="user", uselist=False, cascade="all, delete"
#     )
#     insights = relationship(
#         "Insights", back_populates="user", uselist=False, cascade="all, delete"
#     )
    



class PendingUser(Base):
    __tablename__ = "pending_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    phone_number: Mapped[str] = mapped_column(
        String, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String, nullable=False)
    username: Mapped[str] = mapped_column(String, nullable=False)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[RoleEnum] = mapped_column(
        SQLEnum(RoleEnum), default=RoleEnum.USER, nullable=False)
    language_preference: Mapped[LanguageEnum] = mapped_column(
        SQLEnum(LanguageEnum), default=LanguageEnum.ENGLISH, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(
        "users.id", ondelete="CASCADE"), unique=True)
    age: Mapped[Optional[int]] = mapped_column(Integer)
    cycle_length: Mapped[Optional[int]] = mapped_column(Integer)
    last_period_date: Mapped[Optional[date]] = mapped_column(Date)
    ttc_history: Mapped[Optional[str]] = mapped_column(String)
    faith_preference: Mapped[Optional[str]] = mapped_column(String)
    audio_preference: Mapped[Optional[bool]] = mapped_column(Boolean)

    user: Mapped["Users"] = relationship("Users", back_populates="profile")


class PasswordResetToken(Base):
    __tablename__ = "password_reset_token"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    token: Mapped[str] = mapped_column(String, unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class OTP(Base):
    __tablename__ = "otp"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    verification_id: Mapped[str] = mapped_column(
        String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    phone: Mapped[str] = mapped_column(String, nullable=False)
    otp_hashed: Mapped[str] = mapped_column(String, nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class CashedTranslations(Base):
  __tablename__ = "cached_translations"

  id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
  original_text: Mapped[str] = mapped_column(Text, nullable=False)
  translated_text: Mapped[str] = mapped_column(Text, nullable=False)
  language: Mapped[str] = mapped_column(String(10), nullable=False)

class Cycles(Base):
    __tablename__ = "cycles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(
        "users.id", ondelete="CASCADE"), unique=True)

    last_period_date: Mapped[Date] = mapped_column(Date, nullable=False)
    cycle_length: Mapped[int] = mapped_column(Integer, default=28)
    period_length: Mapped[int] = mapped_column(Integer, default=5)

    symptoms: Mapped[List[str]] = mapped_column(JSON, default=list)

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

    symptoms: Mapped[List[str]] = mapped_column(JSON, default=list)
    insight_text: Mapped[str] = mapped_column(Text, nullable=False)

    user: Mapped["Users"] = relationship("Users", back_populates="insights")
