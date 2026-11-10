from django import forms
from .models import Employee, SalaryPayment


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['employee_id', 'name', 'designation', 'phone', 'email', 'basic_salary', 'status', 'joining_date']
        widgets = {
            'employee_id': forms.TextInput(attrs={'placeholder': 'e.g. EMP-006', 'class': 'w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 outline-none'}),
            'name': forms.TextInput(attrs={'placeholder': 'Full Name', 'class': 'w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 outline-none'}),
            'designation': forms.Select(attrs={'class': 'w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 outline-none'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Phone Number', 'class': 'w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 outline-none'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email Address (optional)', 'class': 'w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 outline-none'}),
            'basic_salary': forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0.00', 'class': 'w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 outline-none'}),
            'status': forms.Select(attrs={'class': 'w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 outline-none'}),
            'joining_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 outline-none'}),
        }


class SalaryPaymentForm(forms.ModelForm):
    class Meta:
        model = SalaryPayment
        fields = ['employee', 'month_year', 'basic_salary', 'allowances', 'overtime_pay', 'deductions', 'payment_date', 'payment_method', 'payment_status', 'remarks']
        widgets = {
            'employee': forms.Select(attrs={'class': 'w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 outline-none'}),
            'month_year': forms.TextInput(attrs={'placeholder': 'e.g. November 2026', 'class': 'w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 outline-none'}),
            'basic_salary': forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0.00', 'class': 'w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 outline-none'}),
            'allowances': forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0.00', 'class': 'w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 outline-none'}),
            'overtime_pay': forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0.00', 'class': 'w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 outline-none'}),
            'deductions': forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0.00', 'class': 'w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 outline-none'}),
            'payment_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 outline-none'}),
            'payment_method': forms.Select(attrs={'class': 'w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 outline-none'}),
            'payment_status': forms.Select(attrs={'class': 'w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 outline-none'}),
            'remarks': forms.TextInput(attrs={'placeholder': 'Payment notes or transfer reference...', 'class': 'w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 outline-none'}),
        }
