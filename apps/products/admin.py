from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['is_active']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ['name', 'sku', 'category', 'selling_price', 'cost_price', 'stock_quantity', 'unit', 'shelf_life_days', 'is_active']
    search_fields = ['name', 'sku']
    list_filter = ['category', 'unit', 'is_active']
    list_editable = ['selling_price', 'stock_quantity', 'is_active']
