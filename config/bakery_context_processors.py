from apps.inventory.models import RawMaterial
from apps.orders.models import CustomCakeOrder
from django.db.models import F


def bakery_notifications(request):
    """
    Real-time Bakery Notifications for Header Bell:
    - Low stock alerts for raw bakery ingredients
    - Upcoming custom cake delivery alerts
    """
    if not request.user.is_authenticated:
        return {}

    try:
        # Low raw material stock items
        low_stock_materials = list(
            RawMaterial.objects.filter(current_stock__lte=F('min_stock_alert'))[:5]
        )
        
        # Upcoming custom cakes pending delivery
        upcoming_cakes = list(
            CustomCakeOrder.objects.filter(
                order__status__in=['booked', 'baking', 'ready']
            ).select_related('order', 'order__customer').order_by('delivery_date')[:5]
        )

        total_alerts = len(low_stock_materials) + len(upcoming_cakes)

        return {
            'header_notifications': {
                'low_stock_materials': low_stock_materials,
                'upcoming_cakes': upcoming_cakes,
                'total_alerts': total_alerts,
                'has_alerts': total_alerts > 0,
            }
        }
    except Exception:
        return {'header_notifications': {'total_alerts': 0, 'has_alerts': False}}
