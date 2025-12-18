from datetime import date


def generate_insight_key(
    *,
    today: date,
    ovulation_day: date,
    fertile_start: date,
    fertile_end: date,
    fertility_score: int
) -> str:
    """Return a key for translation based on cycle info."""

    if today == ovulation_day:
        return "OVULATION_DAY"
    elif fertile_start <= today <= fertile_end:
        return "FERTILE_WINDOW"
    elif fertility_score >= 75:
        return "HIGH_FERTILITY"
    else:
        return "DEFAULT"
