from django.conf import settings
from django.utils.translation import get_language


def get_translated_field(translations: dict[str, str], lang_code: str = None) -> str:
    """
    Get the translated field value using if/else fallback logic.
    """

    # Check the specific language requested
    if lang_code and lang_code in translations:
        return translations[lang_code]

    # Check the current active session language
    active_lang = get_language()
    if active_lang in translations:
        return translations[active_lang]

    # Check the project's default language
    default_lang = settings.LANGUAGE_CODE
    if default_lang in translations:
        return translations[default_lang]

    # Fallback to any available translation
    if translations:
        return next(iter(translations.values()))

    # Ultimate fallback if dictionary is empty
    return ""
