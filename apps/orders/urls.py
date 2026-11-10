from django.urls import path
from . import views

urlpatterns = [
    path('', views.pos_terminal, name='pos_terminal'),
    path('checkout/', views.pos_checkout, name='pos_checkout'),
    path('receipt/<str:order_number>/', views.order_receipt, name='order_receipt'),
    path('custom-cakes/', views.custom_cakes_list, name='custom_cakes_list'),
    path('custom-cakes/create/', views.custom_cake_create, name='custom_cake_create'),
    path('custom-cakes/<int:pk>/status/', views.custom_cake_status_update, name='custom_cake_status_update'),
    path('customers/', views.customers_list, name='customers_list'),
    path('customers/create/', views.customer_create, name='customer_create'),
]
