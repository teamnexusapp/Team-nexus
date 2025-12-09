from datetime import datetime
from database import Base
from sqlalchemy import Column, Date, DateTime, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from schema import Prediction


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    role = Column(String)
    phone_number = Column(String)
    profile = relationship("UserProfile", back_populates="user",
                           uselist=False, cascade="all, delete")
    cycle = relationship("Cycle", back_populates="user",
                         uselist=False, cascade="all, delete")
    insights = relationship("Insights", back_populates="user",
                         uselist=False, cascade="all, delete")


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


class Cycle(Base):
    __tablename__ = "cycles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)

    start_date = Column(Date, nullable=False)
    cycle_length = Column(Integer, default=28)
    period_length = Column(Integer, default=5)

    user = relationship("Users", back_populates="cycle")
    

class Insights(Base):
    __tablename__ = "insights"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), unique=True)

    next_period = Column(Date, nullable=False)
    ovulation_day = Column(Date, nullable=False)
    fertile_period_start= Column(Date, nullable=False)
    fertile_period_end = Column(Date, nullable=False)
    symptoms: Prediction

    user = relationship("Users", back_populates="insights")



