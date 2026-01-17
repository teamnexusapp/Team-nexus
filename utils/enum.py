from enum import Enum


class LanguageEnum(str, Enum):
    ENGLISH = "en"
    YORUBA = "yo"
    IGBO = "ig"
    HAUSA = "ha"
    PIDGIN = "pg"


class RoleEnum(str, Enum):
    USER = "user"
    ADMIN = "admin"


class Symptom(str, Enum):
    headache = "headache"
    nausea = "nausea"
    cramps = "cramps"
    fatigue = "fatigue"
    breast_tenderness = "breast_tenderness"
    acne = "acne"
