from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import RawMaterial, StockMovement


@admin.register(RawMaterial)
class RawMaterialAdmin(ModelAdmin):
    list_display = ['name', 'unit', 'current_stock', 'min_stock_alert', 'unit_cost', 'supplier_name']
    search_fields = ['name', 'supplier_name']
    list_filter = ['unit']
    list_editable = ['current_stock', 'min_stock_alert', 'unit_cost']


@admin.register(StockMovement)
class StockMovementAdmin(ModelAdmin):
    list_display = ['material', 'movement_type', 'quantity', 'unit_cost', 'total_cost', 'date', 'created_at']
    search_fields = ['material__name', 'note']
    list_filter = ['movement_type', 'date']
