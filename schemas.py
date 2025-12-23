from pydantic import BaseModel, Field, EmailStr
from datetime import date, datetime
from typing import List, Optional
from utils.enum import LanguageEnum, RoleEnum, Symptom
from sqlalchemy import String


class CreateUserRequest(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=40, )
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    password: str = Field(..., min_length=8, max_length=60)
    role: Optional[RoleEnum] = RoleEnum.USER
    phone_number: str
    language_preference: Optional[LanguageEnum] = LanguageEnum.ENGLISH


class UserVerify(BaseModel):
    email: str


class UpdateUserProfileRequest(BaseModel):
    age: int
    cycle_length: int
    last_period_date: date
    ttc_history: Optional[str] = None
    faith_preference: str
    audio_preference: Optional[bool] = None


class UserProfileResponse(BaseModel):
    user_id: int
    age: Optional[int] = None
    cycle_length: Optional[int] = None
    last_period_date: Optional[date] = None
    ttc_history: Optional[str] = None
    faith_preference: Optional[str] = None
    audio_preference: Optional[bool] = None

    class Config:
        from_attributes = True

    
    
class LoginRequest(BaseModel):
        email: str
        password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str 
    new_password: str = Field(..., min_length=8)


class CycleRequest(BaseModel):
    last_period_date: date
    cycle_length: int = Field(..., ge=21, le=32)
    period_length: int = Field(..., ge=2, le=10)
    symptoms: List[Symptom] = Field(default_factory=list)


class CycleResponse(BaseModel):
    last_period_date: date
    cycle_length: int
    period_length: int
    symptoms: List[Symptom] = Field(default_factory=list)

    class Config:
        from_attributes = True


class CyclePrediction(BaseModel):
    period_start: str
    period_end: str
    period_length: int
    next_period: str
    ovulation_day: str
    fertile_window: List[str]
    fertility_score: int


class Prediction(BaseModel):
    phase: str
    common_symptoms: list[str]
    recommendations: list[str]


class InsightsRequest(BaseModel):
    cycle_length: int
    last_period_date: date
    period_length: int
    symptoms: List[str] = Field(default_factory=list)


class InsightsResponse(BaseModel):
    next_period: str
    ovulation_day: str
    fertile_period_start:str
    fertile_period_end: str
    symptoms: List[str] = Field(default_factory=list)
     


class MessageRequest(BaseModel):
    message: str


class MessageResponse(BaseModel):
    reply: str


class Token(BaseModel):
    access_token: str
    token_type: str
