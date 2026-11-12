from django.urls import path
from . import views

urlpatterns = [
    path('', views.inventory_list, name='inventory_list'),
    path('material/create/', views.material_create, name='material_create'),
    path('movement/create/', views.stock_movement_create, name='stock_movement_create'),
    
    # Production Batches & BOM
    path('production/', views.production_batches_list, name='production_batches_list'),
    path('production/create/', views.production_batch_create, name='production_batch_create'),
    path('production/reports/', views.production_reports, name='production_reports'),
]
