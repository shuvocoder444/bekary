import uuid
from django.db import models
from django.utils import timezone


class Employee(models.Model):
    DESIGNATION_CHOICES = (
        ('Head Baker', 'Head Baker'),
        ('Pastry Chef', 'Pastry Chef'),
        ('Kitchen Assistant', 'Kitchen Assistant / Helper'),
        ('Cashier', 'Cashier / POS Operator'),
        ('Store Manager', 'Store Manager'),
        ('Delivery Driver', 'Delivery Driver'),
        ('Cleaner', 'Cleaner / Support Staff'),
    )

    STATUS_CHOICES = (
        ('active', 'Active'),
        ('on_leave', 'On Leave'),
        ('resigned', 'Resigned / Inactive'),
    )

    employee_id = models.CharField(max_length=20, unique=True, help_text='Unique Employee ID e.g. EMP-101')
    name = models.CharField(max_length=150)
    designation = models.CharField(max_length=50, choices=DESIGNATION_CHOICES)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    joining_date = models.DateField(default=timezone.now)
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2, help_text='Monthly fixed basic salary')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Bakery Employee'
        verbose_name_plural = 'Bakery Employees'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.designation} ({self.employee_id})"


class SalaryPayment(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('mobile_banking', 'Mobile Banking (bKash/Nagad)'),
    )

    PAYMENT_STATUS_CHOICES = (
        ('paid', 'Paid'),
        ('pending', 'Pending Approval'),
    )

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='salary_payments')
    month_year = models.CharField(max_length=50, help_text='e.g. November 2026')
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text='Bonus, Food, Transport allowances')
    overtime_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text='Overtime or holiday baking duty')
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text='Advance salary, penalties, or absence')
    net_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_date = models.DateField(default=timezone.now)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='paid')
    payslip_number = models.CharField(max_length=50, unique=True, editable=False)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Salary & Payroll Payment'
        verbose_name_plural = 'Salary & Payroll Payments'
        ordering = ['-payment_date', '-created_at']

    def save(self, *args, **kwargs):
        self.net_salary = (self.basic_salary + self.allowances + self.overtime_pay) - self.deductions
        if not self.payslip_number:
            date_str = timezone.now().strftime("%Y%m")
            random_suffix = uuid.uuid4().hex[:4].upper()
            self.payslip_number = f"PAY-{date_str}-{random_suffix}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.payslip_number} - {self.employee.name} ({self.month_year}: {self.net_salary})"
