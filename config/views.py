from django.http import JsonResponse
from django.db import connection
from django.utils import timezone


def health_check(request):
    """
    Production health check endpoint for monitoring, Docker, and Kubernetes probes.
    Validates database connectivity and service availability.
    """
    db_ok = True
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
    except Exception as e:
        db_ok = False

    status_code = 200 if db_ok else 503
    return JsonResponse({
        "status": "healthy" if db_ok else "unhealthy",
        "database": "connected" if db_ok else "disconnected",
        "timestamp": timezone.now().isoformat(),
    }, status=status_code)
