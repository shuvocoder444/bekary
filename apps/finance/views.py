from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from .models import Transaction, AccountHead, LedgerEntry
from .forms import TransactionForm, AccountHeadForm


ALLOWED_CATEGORY_REDIRECTS = {'transactions_list', 'finance_categories'}


def _first_form_error(form):
    for field, errors in form.errors.items():
        if errors:
            return errors[0]
    return 'Please check the form inputs.'


@login_required(login_url='/login/')
def transactions_list(request):
    t_type = request.GET.get('type')
    head_id = request.GET.get('head')

    transactions = Transaction.objects.select_related('account_head').all().order_by('-date', '-created_at')

    if t_type:
        transactions = transactions.filter(transaction_type=t_type)
    if head_id:
        transactions = transactions.filter(account_head_id=head_id)

    total_income = Transaction.objects.filter(transaction_type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = Transaction.objects.filter(transaction_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    net_profit = total_income - total_expense

    account_heads = AccountHead.objects.filter(is_active=True)
    form = TransactionForm()
    category_form = AccountHeadForm()

    context = {
        'transactions': transactions[:50],
        'total_income': total_income,
        'total_expense': total_expense,
        'net_profit': net_profit,
        'account_heads': account_heads,
        'selected_type': t_type,
        'selected_head': head_id,
        'form': form,
        'category_form': category_form,
    }
    return render(request, 'pages/finance_transactions.html', context)


@login_required(login_url='/login/')
def transaction_create(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST, request.FILES)
        if form.is_valid():
            txn = form.save(commit=False)
            txn.created_by = request.user
            txn.save()
            messages.success(request, f"{txn.get_transaction_type_display()} of ৳{txn.amount} recorded successfully!")
        else:
            messages.error(request, 'Error recording transaction. Please check the inputs.')
    return redirect('transactions_list')


@login_required(login_url='/login/')
def categories_list(request):
    head_type = request.GET.get('type')
    categories = AccountHead.objects.annotate(transaction_count=Count('transactions')).order_by('head_type', 'name')

    if head_type:
        categories = categories.filter(head_type=head_type)

    all_heads = AccountHead.objects.all()
    context = {
        'categories': categories,
        'selected_type': head_type,
        'form': AccountHeadForm(),
        'total_count': all_heads.count(),
        'income_count': all_heads.filter(head_type='income').count(),
        'expense_count': all_heads.filter(head_type='expense').count(),
        'active_count': all_heads.filter(is_active=True).count(),
    }
    return render(request, 'pages/finance_categories.html', context)


@login_required(login_url='/login/')
def category_create(request):
    next_route = request.POST.get('next', 'finance_categories')
    if next_route not in ALLOWED_CATEGORY_REDIRECTS:
        next_route = 'finance_categories'

    if request.method == 'POST':
        data = request.POST.copy()
        if 'is_active' not in data:
            data['is_active'] = 'on'
        form = AccountHeadForm(data)
        if form.is_valid():
            head = form.save()
            messages.success(request, f'Category "{head.name}" ({head.get_head_type_display()}) created successfully!')
        else:
            messages.error(request, _first_form_error(form))
    return redirect(next_route)


@login_required(login_url='/login/')
def category_edit(request, pk):
    head = get_object_or_404(AccountHead, pk=pk)
    if request.method == 'POST':
        form = AccountHeadForm(request.POST, instance=head)
        if form.is_valid():
            form.save()
            messages.success(request, f'Category "{head.name}" updated successfully!')
        else:
            messages.error(request, _first_form_error(form))
    return redirect('finance_categories')


@login_required(login_url='/login/')
def category_toggle(request, pk):
    head = get_object_or_404(AccountHead, pk=pk)
    if request.method == 'POST':
        head.is_active = not head.is_active
        head.save(update_fields=['is_active'])
        state = 'activated' if head.is_active else 'deactivated'
        messages.success(request, f'Category "{head.name}" {state}.')
    return redirect('finance_categories')


@login_required(login_url='/login/')
def category_delete(request, pk):
    head = get_object_or_404(AccountHead, pk=pk)
    if request.method == 'POST':
        if head.transactions.exists() or head.ledger_entries.exists():
            messages.error(request, f'Cannot delete "{head.name}" because it is used in existing transactions. Deactivate it instead.')
        else:
            name = head.name
            head.delete()
            messages.success(request, f'Category "{name}" deleted.')
    return redirect('finance_categories')


@login_required(login_url='/login/')
def general_ledger(request):
    head_id = request.GET.get('head')
    entries = LedgerEntry.objects.select_related('account_head').all().order_by('-transaction_date', '-id')

    if head_id:
        entries = entries.filter(account_head_id=head_id)

    total_debit = entries.aggregate(Sum('debit'))['debit__sum'] or 0
    total_credit = entries.aggregate(Sum('credit'))['credit__sum'] or 0
    last_balance = entries.first().running_balance if entries.exists() else 0

    account_heads = AccountHead.objects.filter(is_active=True)

    context = {
        'entries': entries[:100],
        'total_debit': total_debit,
        'total_credit': total_credit,
        'net_balance': last_balance,
        'account_heads': account_heads,
        'selected_head': head_id,
    }
    return render(request, 'pages/general_ledger.html', context)
