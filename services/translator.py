from utils.translations import TRANSLATIONS


def translate_insight(key: str, language: str) -> str:
    """Translate an insight key into the selected language."""
    lang = language.lower()  # e.g., 'yo', 'ig', 'ha','pg'
    return TRANSLATIONS.get(lang, {}).get(key, key)
