import json
from config.translations import TRANSLATIONS, translate_text


def language_context(request):
    """
    Exposes active language ('en' or 'bn') and translations dictionary
    to all Django templates, HTMX fragments, and Alpine.js.
    """
    # 1. Check session
    lang = request.session.get('django_language')

    # 2. Check cookie if session unset
    if not lang:
        lang = request.COOKIES.get('django_language')

    # Default to 'en'
    if lang not in ['en', 'bn']:
        lang = 'en'

    return {
        'current_lang': lang,
        'is_bangla': lang == 'bn',
        'is_english': lang == 'en',
        'translations_json': json.dumps(TRANSLATIONS, ensure_ascii=False),
    }
