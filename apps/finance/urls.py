from django.urls import path
from . import views

urlpatterns = [
    path('', views.transactions_list, name='transactions_list'),
    path('create/', views.transaction_create, name='transaction_create'),
    path('ledger/', views.general_ledger, name='general_ledger'),
]
