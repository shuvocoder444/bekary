from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from apps.finance.models import AccountHead, Transaction
from .models import Employee, SalaryPayment
from .forms import EmployeeForm, SalaryPaymentForm


@login_required(login_url='/login/')
def payroll_dashboard(request):
    employees = Employee.objects.all().order_by('name')
    all_payments = SalaryPayment.objects.select_related('employee').all()

    total_employees = employees.filter(status='active').count()
    monthly_payroll_budget = employees.filter(status='active').aggregate(Sum('basic_salary'))['basic_salary__sum'] or 0
    total_disbursed = all_payments.filter(payment_status='paid').aggregate(Sum('net_salary'))['net_salary__sum'] or 0

    emp_form = EmployeeForm()
    pay_form = SalaryPaymentForm()

    context = {
        'employees': employees,
        'payments': all_payments[:30],
        'total_employees': total_employees,
        'monthly_payroll_budget': monthly_payroll_budget,
        'total_disbursed': total_disbursed,
        'emp_form': emp_form,
        'pay_form': pay_form,
    }
    return render(request, 'pages/payroll_dashboard.html', context)


@login_required(login_url='/login/')
def employee_create(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            emp = form.save()
            messages.success(request, f'Employee "{emp.name}" ({emp.designation}) added successfully!')
        else:
            messages.error(request, 'Error saving employee. Please check inputs.')
    return redirect('payroll_dashboard')


@login_required(login_url='/login/')
def salary_payment_create(request):
    if request.method == 'POST':
        form = SalaryPaymentForm(request.POST)
        if form.is_valid():
            payment = form.save()

            # If payment is marked as 'paid', auto-record an expense transaction in Finance
            if payment.payment_status == 'paid':
                head, _ = AccountHead.objects.get_or_create(
                    name="Employee Salaries & Wages",
                    defaults={'head_type': 'expense', 'is_active': True}
                )
                Transaction.objects.create(
                    transaction_type='expense',
                    account_head=head,
                    title=f"Salary Disbursal: {payment.employee.name} ({payment.month_year})",
                    amount=payment.net_salary,
                    payment_method=payment.payment_method if payment.payment_method in ['cash', 'bank', 'mobile_banking'] else 'bank',
                    date=payment.payment_date,
                    reference_payroll=payment,
                    created_by=request.user,
                    notes=f"Payslip #{payment.payslip_number}. Basic: ৳{payment.basic_salary}, Allowances: ৳{payment.allowances}, Overtime: ৳{payment.overtime_pay}, Deductions: ৳{payment.deductions}."
                )

            messages.success(request, f'Salary payment of ৳{payment.net_salary} processed for {payment.employee.name}!')
            return redirect('payslip_view', payslip_number=payment.payslip_number)
        else:
            messages.error(request, 'Error processing salary payment.')
    return redirect('payroll_dashboard')


@login_required(login_url='/login/')
def payslip_view(request, payslip_number):
    payment = get_object_or_404(SalaryPayment.objects.select_related('employee'), payslip_number=payslip_number)
    return render(request, 'pages/payslip_view.html', {'payment': payment})
