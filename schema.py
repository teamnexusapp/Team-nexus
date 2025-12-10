from pydantic import BaseModel, Field, EmailStr
from datetime import date, datetime
from typing import List, Optional
from enum import Enum
from sqlalchemy import String



class CreateUserRequest(BaseModel):
    email: EmailStr
    username: str = Field(String(40))
    first_name: str
    last_name: str
    password: str = Field(String(40))
    role:str
    phone_number:str


class  UpdateUserProfileRequest(BaseModel):
    age:int
    cycle_length: int
    last_period_date: date
    ttc_history: Optional[str] = None
    faith_preference:str
    language_preference: str
    audio_perference: bool


class UserProfileResponse(BaseModel):
    user_id: int
    age: Optional[int] = None
    cycle_length: Optional[int] = None
    last_period_date: Optional[date] = None
    ttc_history: Optional[str] = None
    faith_preference: Optional[str] = None
    language_preference: Optional[str] = None
    audio_preference: Optional[bool] = None

    class Config:
        from_attributes = True


class Symptom(str, Enum):
    headache = "headache"
    nausea = "nausea"
    cramps = "cramps"
    fatigue = "fatigue"
    breast_tenderness = "breast_tenderness"
    acne = "acne"



class CycleRequest(BaseModel):
    last_period_date: date
    cycle_length : int = Field(..., ge=21, le=32)
    period_length: int = Field(..., ge=2, le=10)
    symptoms: Optional[List[Symptom]] = None


class CycleResponse(BaseModel):
    last_period_date: date
    cycle_length: int
    period_length: int
    symptons: Optional[List[Symptom]]

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
    period_length:int
    symptoms: dict | None = None


class MessageRequest(BaseModel):
    message: str

class Token(BaseModel):
    access_token: str
    token_type: str
 
