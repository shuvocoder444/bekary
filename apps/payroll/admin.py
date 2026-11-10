from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Employee, SalaryPayment


@admin.register(Employee)
class EmployeeAdmin(ModelAdmin):
    list_display = ['employee_id', 'name', 'designation', 'phone', 'basic_salary', 'status', 'joining_date']
    search_fields = ['employee_id', 'name', 'phone', 'email']
    list_filter = ['designation', 'status', 'joining_date']
    list_editable = ['status', 'basic_salary']


@admin.register(SalaryPayment)
class SalaryPaymentAdmin(ModelAdmin):
    list_display = ['payslip_number', 'employee', 'month_year', 'basic_salary', 'allowances', 'overtime_pay', 'deductions', 'net_salary', 'payment_date', 'payment_status', 'payment_method']
    search_fields = ['payslip_number', 'employee__name', 'employee__employee_id']
    list_filter = ['payment_status', 'payment_method', 'month_year', 'payment_date']
