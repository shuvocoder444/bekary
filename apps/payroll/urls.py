from django.urls import path
from . import views

urlpatterns = [
    path('', views.payroll_dashboard, name='payroll_dashboard'),
    path('employee/create/', views.employee_create, name='employee_create'),
    path('salary/disburse/', views.salary_payment_create, name='salary_payment_create'),
    path('payslip/<str:payslip_number>/', views.payslip_view, name='payslip_view'),
]
