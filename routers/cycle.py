from datetime import datetime, timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from starlette import status
from models import Cycle, Users, UserProfile
from database import SessionLocal
from schema import CycleRequest, UpdateUserProfileRequest, UserProfileResponse
from .auth import get_current_user
from passlib.context import CryptContext


router = APIRouter(
    prefix="/cycle",
    tags=["cycle"]
)


# create a db dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# create the API dependencies


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def cycle_calculate(start_date:datetime, cycle_length:int, period_length:int):
    if isinstance(start_date, datetime):
        start_date = start_date.date()

    ovulation_day = start_date + timedelta(days=cycle_length-14)
    fertilation_start = ovulation_day - timedelta(days=5)
    fertilation_end = ovulation_day + timedelta(days=1)
    next_period = start_date + timedelta(days=cycle_length)
    period_end = start_date + timedelta(days=cycle_length)

    return {
        "ovulation_day": ovulation_day,
        "fertile_window": {
            "start":  fertilation_start,
            "end": fertilation_end,
        },
        "next_period": next_period,
        "period_end":period_end
    }




@router.post("/calculate_cycle", status_code=status.HTTP_200_OK)
async def calculate_cycle(cycle_data: CycleRequest, db: db_dependency, user: user_dependency ):
    user_id = user['id']
    cycle_info = cycle_calculate(
        start_date=cycle_data.start_date,
        cycle_length=cycle_data.cycle_length,
        period_length=cycle_data.period_length
    )

    cycle = Cycle(
           user_id=user_id,
           start_date=cycle_data.start_date,
           cycle_length=cycle_data.cycle_length,
           period_length=cycle_data.period_length

       )

    db.add(cycle)
    db.commit()
    db.refresh(cycle)
    return cycle_info