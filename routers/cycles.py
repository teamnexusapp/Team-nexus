from datetime import datetime, timedelta, date
from datetime import datetime, timedelta
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from starlette import status
from models import Cycles
from database import SessionLocal
from schemas import CycleRequest, UpdateUserProfileRequest, UserProfileResponse, CycleResponse
from passlib.context import CryptContext
from utils.predictions import simple_fertility_ai
from utils.utils import get_current_user


router = APIRouter(
    prefix="/cycle",
    tags=["cycle"]
)



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/cycles", status_code=status.HTTP_200_OK, response_model=List[CycleResponse])
async def get_cycle(db:db_dependency, user:user_dependency):
    cycles_list = db.query(Cycles).filter(Cycles.user_id == user['id']).all()

    if not cycles_list:
        raise HTTPException(
            status_code=404,
            detail="No cycles found for this user."
        )
      
    return [
        {
            "Cycle_id": cycle.id,
            "last_period_date": cycle.last_period_date,
            "Cycle_length": cycle.cycle_length,
            "Period_length": cycle.period_length
        }
        for cycle in cycles_list
    ]



@router.post("/cycles", status_code=status.HTTP_200_OK, response_model=dict)
async def cycles(cycle_data: CycleRequest, db: db_dependency, user: user_dependency ):
    user_id = user['id']
    cycle_info = simple_fertility_ai(
        last_period_date=cycle_data.last_period_date,
        cycle_length=cycle_data.cycle_length,
        period_length=cycle_data.period_length,
        symptoms=cycle_data.symptoms
    )

    cycle = Cycles(
           user_id=user_id,
           last_period_date=cycle_data.last_period_date,
           cycle_length=cycle_data.cycle_length,
           period_length=cycle_data.period_length,
           symptoms=cycle_data.symptoms

       )

    db.add(cycle)
    db.commit()
    db.refresh(cycle)
    return cycle_info


