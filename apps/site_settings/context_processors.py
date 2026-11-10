from django.core.cache import cache
from .models import SiteSetting


def site_settings(request):
    """
    Performance-optimized context processor with Low-Level Caching.
    In-memory caching prevents database hit on every HTTP request.
    """
    setting = cache.get('global_site_setting')
    if setting is None:
        try:
            setting = SiteSetting.objects.first()
        except Exception:
            setting = None
        cache.set('global_site_setting', setting, 3600)  # Cache for 1 hour (3600 seconds)
    return {'site_setting': setting}
