from pydantic import BaseModel, Field, EmailStr
from datetime import date
from typing import Optional

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

class CycleRequest(BaseModel):
    start_date : date
    cycle_length : int = Field(..., ge=21, le=32)
    period_length: int = Field(..., ge=2, le=10)


class Token(BaseModel):
    access_token: str
    token_type: str
 
