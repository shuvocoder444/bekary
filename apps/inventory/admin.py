from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import RawMaterial, StockMovement, ProductionBatch, BatchConsumption, BatchOutput


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


class BatchConsumptionInline(TabularInline):
    model = BatchConsumption
    extra = 1
    fields = ['material', 'quantity', 'unit_cost', 'total_cost']


class BatchOutputInline(TabularInline):
    model = BatchOutput
    extra = 1
    fields = ['product', 'quantity', 'unit_cost']


@admin.register(ProductionBatch)
class ProductionBatchAdmin(ModelAdmin):
    list_display = ['batch_number', 'production_date', 'status', 'total_raw_material_cost', 'created_by', 'created_at']
    list_filter = ['status', 'production_date']
    search_fields = ['batch_number', 'notes']
    inlines = [BatchConsumptionInline, BatchOutputInline]
