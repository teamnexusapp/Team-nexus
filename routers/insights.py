from typing import Annotated, List
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Insights, Users
from schemas import InsightsRequest, InsightsResponse
from utils.utils import get_current_user
from starlette import status
from utils.predictions import simple_fertility_ai
from services.insights_engine import generate_insight_key
from services.translator import translate_insight


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

router = APIRouter(
    prefix="/insights",
    tags=["insights"]
)


def str_to_date(date_str: str) -> date:
    return datetime.strptime(date_str, "%Y-%m-%d").date()


@router.get("/insights", status_code=status.HTTP_200_OK, response_model=List[InsightsResponse])
async def get_insights(db: db_dependency,user: user_dependency):
    user_insights = (db.query(Insights).filter(
        Insights.user_id == user['id']).all())
    
    return user_insights


@router.post("/insights", status_code=status.HTTP_200_OK)
async def insights(
    data: InsightsRequest,
    db: db_dependency,
    user: user_dependency
):
    db_user = db.query(Users).filter(Users.id == user["id"]).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Please, Sign In")

    try:
        
        prep_result = simple_fertility_ai(
            cycle_length=data.cycle_length,
            last_period_date=data.last_period_date,
            period_length=data.period_length,
            symptoms=data.symptoms
        )

        next_period_date = str_to_date(prep_result["next_period"])
        ovulation_day_date = str_to_date(prep_result["ovulation_day"])
        fertile_start_date = str_to_date(prep_result["fertile_window"][0])
        fertile_end_date = str_to_date(prep_result["fertile_window"][1])
        fertility_score = prep_result["fertility_score"]

    
        key = generate_insight_key(
            today=date.today(),
            ovulation_day=ovulation_day_date,
            fertile_start=fertile_start_date,
            fertile_end=fertile_end_date,
            fertility_score=fertility_score
        )

  
        insight_text = translate_insight(
            key=key,
            language=db_user.language_preference.value
        )

     
        existing_insight = db.query(Insights).filter(
            Insights.user_id == db_user.id
        ).first()

        if existing_insight:
            existing_insight.next_period = next_period_date
            existing_insight.ovulation_day = ovulation_day_date
            existing_insight.fertile_period_start = fertile_start_date
            existing_insight.fertile_period_end = fertile_end_date
            existing_insight.symptoms = data.symptoms
            existing_insight.insight_text = insight_text
            db.commit()
            db.refresh(existing_insight)
            saved_insight = existing_insight
        else:
            new_insight = Insights(
                user_id=db_user.id,
                next_period=next_period_date,
                ovulation_day=ovulation_day_date,
                fertile_period_start=fertile_start_date,
                fertile_period_end=fertile_end_date,
                symptoms=data.symptoms,
                insight_text=insight_text
            )
            db.add(new_insight)
            db.commit()
            db.refresh(new_insight)
            saved_insight = new_insight

        return {
            "predictions": prep_result,
            "insight": saved_insight.insight_text
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Something went wrong: {e}")
