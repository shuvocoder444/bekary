from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from .models import Transaction, AccountHead, LedgerEntry
from .forms import TransactionForm


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

    context = {
        'transactions': transactions[:50],
        'total_income': total_income,
        'total_expense': total_expense,
        'net_profit': net_profit,
        'account_heads': account_heads,
        'selected_type': t_type,
        'selected_head': head_id,
        'form': form,
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
