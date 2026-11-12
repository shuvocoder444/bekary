from django.urls import path
from . import views

urlpatterns = [
    path('', views.transactions_list, name='transactions_list'),
    path('create/', views.transaction_create, name='transaction_create'),
    path('categories/', views.categories_list, name='finance_categories'),
    path('categories/create/', views.category_create, name='finance_category_create'),
    path('categories/<int:pk>/edit/', views.category_edit, name='finance_category_edit'),
    path('categories/<int:pk>/toggle/', views.category_toggle, name='finance_category_toggle'),
    path('categories/<int:pk>/delete/', views.category_delete, name='finance_category_delete'),
    path('ledger/', views.general_ledger, name='general_ledger'),
]
