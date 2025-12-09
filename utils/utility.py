from datetime import datetime, timedelta

from schema import Prediction


def cycle_calculation(start_date: datetime,  period_length: int, cycle_length: int = 28):
    if isinstance(start_date, datetime):
       start_date = start_date.date()

    ovulation_day = start_date + timedelta(days=cycle_length-14)
    fertile_period_start = ovulation_day - timedelta(days=5)
    fertile_period_end = ovulation_day + timedelta(days=1)
    next_period = start_date + timedelta(days=cycle_length)
    period_end = start_date + timedelta(days=cycle_length)

    return {
        "ovulation_day": ovulation_day,
        "fertile_period_start": fertile_period_start,
        "fertile_period_end": fertile_period_end,
        "next_period": next_period,
        "period_end": period_end
    }




def symptoms_and_recommendation( days: int, cycle_length: int) -> Prediction:
    
      if days <= 5:
        
        phase = "Menstrual"
        symptoms = ["cramps", "fatigue",
            "lower back pain", "headache", "mood swings"]
        recommendations = [
            "Stay hydrated",
            "Use a warm pad for cramps",
            "Increase iron-rich foods (spinach, beans, fish)",
            "Light stretching or yoga",
            "Rest as needed"
        ]

      elif 6 <= days <= 13:
       
        phase = "Follicular"
        symptoms = ["increased energy", "clearer mood", "light spotting (sometimes)"]
        recommendations = [
            "Start moderate exercise",
            "Good time for planning and productivity",
            "Eat protein + healthy fats",
            "Stay consistent with sleep"
        ]

      elif 14 <= days <= 16:
        
        phase = "Ovulation"
        symptoms = [
            "increased libido",
            "clear stretchy cervical mucus",
            "light pelvic pain (mittelschmerz)",
            "increased energy"
        ]
        recommendations = [
            "Best time for conception",
            "Stay hydrated",
            "Healthy meals (fruits, vegetables, lean protein)",
            "Avoid heavy stress"
        ]

      else:
        
        phase = "Luteal"
        symptoms = [
            "bloating",
            "breast tenderness",
            "fatigue",
            "irritability",
            "food cravings",
            "mild cramps"
        ]
        recommendations = [
            "Reduce sugar + caffeine",
            "Magnesium-rich foods for mood and cramps",
            "Light exercise helps with PMS",
            "Stay hydrated",
            "Get enough sleep"
        ]

      return Prediction(
        phase=phase,
        common_symptoms=symptoms,
        recommendations=recommendations
    )