from datetime import datetime, timedelta, date


SYMPTOM_SCORES = {
    "egg_white_mucus": 15,
    "ovulation_cramps": 10,
    "high_libido": 8,
    "soft_cervix": 7,
    "fatigue": -5,
    "bloating": -4,
    "headache": -3,
    "back_pain": -4
}


def simple_fertility_ai(
    *,
    cycle_length: int,
    last_period_date: date,
    period_length: int,
    symptoms: list[str] | None
):
    cycle_length = cycle_length or 28
    period_length = period_length or 5 

   
    if isinstance(last_period_date, date):
        last_period = datetime.combine(last_period_date, datetime.min.time())
    else:
        last_period = datetime.strptime(last_period_date, "%Y-%m-%d")

  
    period_start = last_period
    period_end = last_period + timedelta(days=period_length - 1)

  
    next_period = last_period + timedelta(days=cycle_length)
    ovulation = last_period + timedelta(days=cycle_length - 14)

    fertile_window = [
        (ovulation - timedelta(days=2)).strftime("%Y-%m-%d"),
        (ovulation + timedelta(days=2)).strftime("%Y-%m-%d")
    ]

    fertility_score = 80 

    if symptoms:
        for s in symptoms:
            if s in SYMPTOM_SCORES:
                fertility_score += SYMPTOM_SCORES[s]

   
    fertility_score = max(0, min(100, fertility_score))

    return {
        "period_start": period_start.strftime("%Y-%m-%d"),
        "period_end": period_end.strftime("%Y-%m-%d"),
        "period_length": period_length,
        "next_period": next_period.strftime("%Y-%m-%d"),
        "ovulation_day": ovulation.strftime("%Y-%m-%d"),
        "fertile_window": fertile_window,
        "fertility_score": fertility_score
    }
