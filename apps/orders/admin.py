from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline, StackedInline
from .models import Customer, Order, OrderItem, CustomCakeOrder


class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 1


class CustomCakeOrderInline(StackedInline):
    model = CustomCakeOrder
    can_delete = False


@admin.register(Customer)
class CustomerAdmin(ModelAdmin):
    list_display = ['name', 'phone', 'email', 'total_orders', 'total_spent', 'created_at']
    search_fields = ['name', 'phone', 'email']


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ['order_number', 'order_type', 'customer', 'status', 'payment_status', 'payment_method', 'total_amount', 'paid_amount', 'due_amount', 'created_at']
    search_fields = ['order_number', 'customer__name', 'customer__phone']
    list_filter = ['order_type', 'status', 'payment_status', 'payment_method', 'created_at']
    inlines = [OrderItemInline, CustomCakeOrderInline]


@admin.register(CustomCakeOrder)
class CustomCakeOrderAdmin(ModelAdmin):
    list_display = ['order', 'flavor', 'weight_lbs', 'delivery_date', 'delivery_time', 'tier_count']
    search_fields = ['order__order_number', 'flavor', 'cake_message']
    list_filter = ['delivery_date', 'flavor']
