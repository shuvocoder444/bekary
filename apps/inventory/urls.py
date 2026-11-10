from django.urls import path
from . import views

urlpatterns = [
    path('', views.inventory_list, name='inventory_list'),
    path('material/create/', views.material_create, name='material_create'),
    path('movement/create/', views.stock_movement_create, name='stock_movement_create'),
]
