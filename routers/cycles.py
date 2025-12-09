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
from utils.utility import cycle_calculation


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


@router.get("/cycles", status_code=status.HTTP_200_OK)
async def get_cylces(db:db_dependency, user:user_dependency):
    cycles_list = db.query(cycles).filter(cycles.user_id == user['id']).all()

    if not cycles_list:
        raise HTTPException(
            status_code=404,
            detail="No cycles found for this user."
        )
      
    return [ {
          "Cycle_id": cycle.id,
          "Start_date": cycle.start_date,
          "Cycle_length": cycle.cycle_length,
          "Period_length": cycle.period_length
           
       }

        for cycle in cycles_list
]


@router.post("/cycles", status_code=status.HTTP_200_OK)
async def cycles(cycle_data: CycleRequest, db: db_dependency, user: user_dependency ):
    user_id = user['id']
    cycle_info = cycle_calculation(
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