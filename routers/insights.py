from datetime import datetime, timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from starlette import status
from models import Cycle, Insights, Users, UserProfile
from database import SessionLocal
from schema import CycleRequest, InsightsRequest, UpdateUserProfileRequest, UserProfileResponse
from utils.utility import cycle_calculation, symptoms_and_recommendation
from .auth import get_current_user
from passlib.context import CryptContext


router = APIRouter(
    prefix="/insights",
    tags=["insights"]
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


@router.get("/insights", status_code=status.HTTP_200_OK, response_model=InsightsRequest)
async def get_insights(db: db_dependency, user: user_dependency):
   insights_list = db.query(Insights).filter(Insights.user_id == user['id']).all()

   if not insights_list:
       raise HTTPException(
           status_code=404,
           detail="No cycles found for this user."
       )
    
   last_insight = insights_list[-1]

   start_date = last_insight.start_date
   cycle_length = last_insight.cycle_length
   period_length = last_insight.period_length

   cycle_result = cycle_calculation(start_date, cycle_length, period_length )
   
   today = datetime.now().date()
   days_in_cycle = (today - start_date).days % cycle_length

   symptoms = symptoms_and_recommendation(days_in_cycle, cycle_length)
   
   return {
       "cycle": {
           "ovulation_day": cycle_result["ovulation_day"],
           "fertile_period_start": cycle_result["fertile_period_start"],
           "fertile_period_end": cycle_result["fertile_period_end"],
           "next_period": cycle_result["next_period"],
           "period_end": cycle_result["period_end"]
       },
       "symptoms_and_recommendations": symptoms
   }
