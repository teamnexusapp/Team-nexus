
from schema import InsightsRequest
from fastapi import APIRouter
from utils.ai import hf_generate
from utils.predictions import simple_fertility_ai


router = APIRouter()




@router.post("/insights")
async def insights(data: InsightsRequest):
    try:

        prep_result = simple_fertility_ai(
            cycle_length=data.cycle_length,
            last_period_date=data.last_period_date,
            period_length=data.period_length,
            symptoms=data.symptoms
        )

        prep_result["next_period"] = str(prep_result["next_period"])
        prep_result["ovulation_day"] = str(prep_result["ovulation_day"])
        prep_result["fertile_window"] = [
            str(d) for d in prep_result["fertile_window"]]

        prompt = f"""
These are the fertility predictions:
Next period: {prep_result['next_period']}
Ovulation day: {prep_result['ovulation_day']}
Fertile window: {prep_result['fertile_window']}
Fertility score: {prep_result['fertility_score']}

Write a friendly, supportive, simple fertility insight.
Avoid medical diagnosis.
"""

        insight = hf_generate(prompt)

        return {
            "predictions": prep_result,
            "insight": insight
        }

    except Exception as e:

        return {"error": f"Something went wrong: {e}"}
